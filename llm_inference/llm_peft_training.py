import os
from typing_extensions import get_protocol_members
import yaml
import sys
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling, BitsAndBytesConfig
import datasets
from datasets import DatasetDict
from peft import (
    prepare_model_for_kbit_training,
    LoraConfig,
    get_peft_model,
    PeftConfig,
    PeftModel,
    TaskType,
)
from accelerate import infer_auto_device_map
from peft import prepare_model_for_kbit_training
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)





def main():

    print(torch.cuda.device_count())
    print()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    # Load the config path
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    # LLM setting
    model_id = config_all["llm_params"]["model"]

    model_outdir = config_all['llm_params']['model_outdir']
    model_train_name = config_all["llm_params"]['model_train_name']

    lora_config = config_all["llm_params"]["lora_config"]

    # Loading and preparing the training set
    training_set_path = config_all["llm_params"]["training_set_path"]
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
        model_id,
        padding_side="left",  # Add padding as use less memory for training
        add_eos_token=True,
        add_bos_token=True,
        padding='max_length',
        max_length=15000
    )
    tokenizer.pad_token = tokenizer.unk_token
    # Need to be 'input_ids' to be passed to a SFTTrainer trainer class
    tokenized_train_ds = training_set.map(lambda x: {"input_ids": tokenizer.apply_chat_template(x["message"], tokenize=True, add_generation_prompt=False)})
    # Getting the max token length from the training set and adjust that as padding length
    max_length = max([len(x) for x in tokenized_train_ds['training']['input_ids']])
    print(max_length)

    # Retokenized with the max token length
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        padding_side="left",  # Add padding as use less memory for training
        add_eos_token=True,
        add_bos_token=True,
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )

    tokenizer.pad_token = tokenizer.unk_token

    tokenized_train_ds = training_set.map(lambda x: {"input_ids": tokenizer.apply_chat_template(x["message"], tokenize=True, add_generation_prompt=False)})


    # Load LORA config
    lora_config = config_all["llm_params"]["lora_config"]
    peft_config = LoraConfig(**lora_config)


    # Load bitsandBytes config
    try:
        bits_and_bytes_config = config_all["llm_params"]["bits_and_bytes_config"]
        bits_and_bytes_config["bnb_4bit_compute_dtype"] = torch.float16
        bitsandbytes = BitsAndBytesConfig(**bits_and_bytes_config)
    except KeyError:
        bitsandbytes = None
    
    # Load the model with bitsandbytes
    model = AutoModelForCausalLM.from_pretrained(
      model_id,
      quantization_config=bitsandbytes
    ).to(device)
    # Prepare the model for peft training with the quantization params
    model = prepare_model_for_kbit_training(model)

    # Load the model in peft mode
    model = get_peft_model(model, peft_config)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    # Instantiate the trainer
    config_trainers_params = config_all["llm_params"]["trainer_params"]
    training_args = TrainingArguments(
        output_dir=f"{model_outdir}/{model_train_name}_{model_id}",
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

    trainer.model.save_pretrained(f"{model_outdir}/{model_train_name}_{model_id}")


    # del model
    # del trainer
    
    # # Merging the new model

    # peft_config = PeftModel.from_pretrained(f"{model_outdir}/{model_train_name}")
    # model = AutoModelForCausalLM.from_pretrained(
    #         peft_config.base_model_name_or_path,
    #         quantization_config=bitsandbytes,
    #         low_cpu_mem_usage=True,
    # )
    # model = PeftModel.from_pretrained(
    #         model,
    #         f"{model_outdir}/{model_train_name}",
    #         device_map="auto",
    # )
    # model.eval()
    # os.makedirs(f"{model_outdir}/{model_train_name}_merged", exist_ok=True)

    # merged_model = model.merge_and_unload()
    # merged_model.save_pretrained(f"{model_outdir}/{model_train_name}_merged")

    # tokenizer = AutoTokenizer.from_pretrained(model_id)
    # tokenizer.save_pretrained(f"{model_outdir}/{model_train_name}_merged")


if __name__ == "__main__":
    main()
