import argparse
import os
import sys
import logging
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
import datasets
from datasets import DatasetDict
from peft import (
    prepare_model_for_kbit_training,
    LoraConfig,
    get_peft_model,
)
from peft import prepare_model_for_kbit_training

from utils.utils import (
    print_cuda_state,
    get_arguments,
    load_config,
    setup_model_path,
    setup_adapter_path,
    setup_bits_and_bytes_config,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


def main():

    print_cuda_state()

    parser = argparse.ArgumentParser()
    parser.add_argument("--local_rank", type=int, default=0)
    parser.add_argument("--deepspeed", type=str, default=None)

    parser.add_argument(
        "--model",
        default=None,
        type=str,
        required=False,
        help="Give the config filename to the model to be run. ",
    )

    args = parser.parse_args()
    local_rank = args.local_rank
    deepspeed_config = args.deepspeed
    logger.info(f"Using model: {args.model}")

    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = load_config(config_path)

    config_model_path = os.path.join(
        os.path.dirname(__file__), "../config", f"{args.model}.yaml"
    )
    config_model = load_config(config_model_path)

    model_path = setup_model_path(config_all, config_model)
    adapter_path, adapter_id = setup_adapter_path(model_path, config_model)

    model_quantization = config_model["peft"]["quantization"]
    model_quantization, bitsandbytes = setup_bits_and_bytes_config(
        model_quantization, config_model["bits_and_bytes"]
    )

    model_id = f"{model_path}_{model_quantization}{adapter_id}"
    # LLM setting
    lora_config = config_model["peft"]["lora_config"]

    # Loading and preparing the training set
    training_set_path = config_all["llm_params"]["training_set_path"]
    # FIXME Need to move that into the prep dataset to ensure reproductiblity (but the seed should be enough)
    ds_training_set = datasets.load_from_disk(training_set_path)
    # Split a first time to gain the train set and the test set
    ds_training_set = ds_training_set.train_test_split(
        test_size=0.2, seed=42, stratify_by_column="answer"
    )
    # Split the test set a second time to get the validation set and the test set
    ds_devtest = ds_training_set["test"].train_test_split(
        test_size=0.5, seed=42, stratify_by_column="answer"
    )
    # Create a new DatasetDict to get all of them in one place
    training_set = DatasetDict(
        {
            "training": ds_training_set["train"],
            "validation": ds_devtest["train"],
            "test": ds_devtest["test"],
        }
    )

    # Tokenizing the training set
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        padding_side="left",  # Add padding as use less memory for training
        add_eos_token=True,
        add_bos_token=True,
        # padding="max_length",
        # max_length=15000,
    )
    # To still pad but not training on th pad_token but still on the eos_token
    tokenizer.pad_token = tokenizer.unk_token
    # Need to be 'input_ids' to be passed to a SFTTrainer trainer class
    tokenized_train_ds = training_set.map(
        lambda x: {
            "input_ids": tokenizer.apply_chat_template(
                x["message"], tokenize=True, add_generation_prompt=False
            )
        }
    )
    # Getting the max token length from the training set and adjust that as padding length
    max_length = max([len(x) for x in tokenized_train_ds["training"]["input_ids"]])
    print(max_length)

    # Retokenized with the max token length
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        padding_side="left",  # Add padding as use less memory for training
        add_eos_token=True,
        add_bos_token=True,
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )

    tokenizer.pad_token = tokenizer.unk_token

    tokenized_train_ds = training_set.map(
        lambda x: {
            "input_ids": tokenizer.apply_chat_template(
                x["message"], tokenize=True, add_generation_prompt=False
            )
        }
    )
    # print(tokenized_train_ds['training'][0]['message'])

    # Load LORA config
    peft_config = LoraConfig(**lora_config)

    # Load the model with bitsandbytes
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bitsandbytes,
        # device_map={"": torch.cuda.current_device()},
    )
    # Prepare the model for peft training with the quantization params
    model = prepare_model_for_kbit_training(model)

    # Load the model in peft mode
    model = get_peft_model(model, peft_config)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    # Print the mem used
    print_cuda_state()

    # Instantiate the trainer
    config_trainers_params = config_model["peft"]["trainer_params"]
    training_args = TrainingArguments(
        output_dir=adapter_path,
        local_rank=local_rank,  # Add local_rank to be run in //
        deepspeed=deepspeed_config,
        **config_trainers_params,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_ds["training"],
        eval_dataset=tokenized_train_ds["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()

    # Loading the LORA model
    lora_model = get_peft_model(model, peft_config)
    lora_model.print_trainable_parameters()

    trainer.model.save_pretrained(adapter_path)


if __name__ == "__main__":
    main()
