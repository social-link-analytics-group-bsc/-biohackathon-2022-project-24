import os
from typing_extensions import get_protocol_members
import yaml
import sys
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
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
from trl import SFTTrainer
from accelerate import infer_auto_device_map

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)





def main():

    # Load the config path
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    # LLM setting
    model_id = config_all["llm_params"]["model"]
    # model = AutoModelForCausalLM.from_pretrained(model_id)

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

    # # Retokenized with the max token length
    # tokenizer = AutoTokenizer.from_pretrained(
    #     model_id,
    #     padding_side="left",  # Add padding as use less memory for training
    #     add_eos_token=True,
    #     add_bos_token=True,
    #     truncation=True,
    #     max_length=max_length,
    #     padding="max_length",
    # )

    # tokenized_train_ds = training_set.map(lambda x: {"input_ids": tokenizer.apply_chat_template(x["message"], tokenize=True, add_generation_prompt=False)})


    # Load LORA config
    lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
    model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.float16,
      # device_map='balanced',
      # device_map=device_map,
    )
    model = get_peft_model(model, lora_config)
    # device_map = infer_auto_device_map(model, max_memory={0: "55GiB", 1: "55GiB", "cpu": "30GiB"})
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=f"{model_outdir}/{model_train_name}",
        learning_rate=2e-5,
        per_device_train_batch_size=10,
        per_device_eval_batch_size=10,
        num_train_epochs=3,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        push_to_hub=False,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_ds["training"],
        eval_dataset=tokenized_train_ds["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        # compute_metrics=compute_metrics,
    )

    # trainer = SFTTrainer(
    #     model,
    #     args = training_args,
    #     train_dataset=tokenized_train_ds['training'],
    #     eval_dataset=tokenized_train_ds['validation'],
    #     dataset_text_field="input_ids",
    #     peft_config=lora_config)
    trainer.train()

    # Loading the LORA model
    # lora_model = get_peft_model(model, lora_config)
    # lora_model.print_trainable_parameters()

    trainer.model.save_pretrained(f"{model_outdir}/{model_train_name}")


    del model
    del trainer

    peft_config = PeftModel.from_pretrained(f"{model_outdir}/{model_train_name}")
    model = AutoModelForCausalLM.from_pretrained(
            peft_config.base_model_name_or_path,
            load_in_8bit=False,
            return_dict=True,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
    )
    model = PeftModel.from_pretrained(
            model,
            f"{model_outdir}/{model_train_name}",
            torch_dtype=torch.float16,
            device_map="auto",
    )
    model.eval()
    os.makedirs(f"{model_outdir}/{model_train_name}_merged", exist_ok=True)

    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(f"{model_outdir}/{model_train_name}_merged")

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.save_pretrained(f"{model_outdir}/{model_train_name}_merged")


if __name__ == "__main__":
    main()
