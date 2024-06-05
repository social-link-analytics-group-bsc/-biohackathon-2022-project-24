# To transform the json into the meaninful json answer to train the model.
# Based on Blanca Calvo script and adapted
import os
import sys
import yaml
import collections
import argparse
from datasets import load_dataset, Dataset, ClassLabel

from utils.prompt_instructions import prompt_instruction_3


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def parsing_arguments(parser):
    parser.add_argument(
        "--data",
        type=str,
        default="nothing",
        help="Prodigy data to transform into conll",
    )
    return parser


def _extract_labels(example):
    token_to_label = {}
    try:
        for span in example["spans"]:
            if span["token_start"] == span["token_end"]:
                label = span["label"]
                # FIXME As soon as it is fixed in prodigy, can remove the if
                if label == "n_fem":
                    label = "n_female"
                # if label not in token_to_label.keys():
                #     print(label)
                #     raise
                value = example["tokens"][span["token_start"]]["id"]
                token_to_label.setdefault(label, []).append(value)
            # FIXME no idea what this part does it is Blanca code
            else:
                for r in range(
                    span["token_start"], span["token_end"] + 1
                ):  # TODO: finish this
                    label = span["label"]
                    # FIXME As soon as it is fixed in prodigy, can remove the if
                    if label == "n_fem":
                        label = "n_female"
                    value = example["tokens"][span["token_start"]]["id"]
                    token_to_label.setdefault(label, []).append(value)
    except KeyError:  # if there are no spans
        token_to_label = {}
    example["labels"] = token_to_label
    return example


def _create_full_json_answer(example):
    """
    Create the final answer for the model training.
    No more information is used for the training
    """
    example["answer_training"] = str(
        {"answer": example["answer"], "labels": example["labels"]}
    )
    return example


def _create_prompt(example, prompt_instruction):

    example["prompt_instruction"] = f"""{prompt_instruction}"""
    return example


def _create_chat_data(example):
    example["message"] = [
        {
            "role": "user",
            "content": f"""####Instructions:\n{example['prompt_instruction']}\n####Article\n{example['text']}""",
        },
        {"role": "assistant", "content": example["answer_training"]},
    ]
    return example


def _transform_key_meta(example):
    """
    Rename the embedded key meta.pmcid to pmcid
    """
    example["pmcid"] = example["meta"]["pmcid"]
    return example


def _drop_unused_data(dataset: Dataset) -> Dataset:
    """
    Use the built-in function for dropping columns.
    Need the dataset and not an example here
    Dropping all the columns except:
    - answer: the number associated to the type of answer for stratified sampling
    - answer_training: answer for the model
    - pmcid: pmcid to be able to match the article
    - prompt_instruction: the instruction choose for the model
    - _annotator_id: The annotator in case random on that is important
    - message: formated prompt for training
    - text: original method text
    """
    col_to_drop = [
        "spans",
        "tokens",
        "meta",
        "label",
        "labels",
        "_input_hash",
        "_task_hash",
        "_view_id",
        "_timestamp",
        "_session_id",
    ]
    dataset = dataset.remove_columns(col_to_drop)
    return dataset


def cast_label(dataset: Dataset) -> Dataset:
    """
    Cast the column answer as ClassLabel type to
    stratify in the test/train split
    """
    new_features = dataset.features.copy()
    new_features["answer"] = ClassLabel(names=["accept", "reject", "ignore"])
    dataset = dataset.cast(new_features)
    return dataset


def print_simple_info(dataset):
    print(dataset)
    print(collections.Counter(dataset["answer"]))
    print(collections.Counter(dataset["_annotator_id"]))


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))
    training_set_path = config_all["llm_params"]["training_set_path"]

    dataset = load_dataset("json", data_files=args.data, split="train")
    dataset = dataset.map(_extract_labels)
    # Not using the reason (transforming short answer to long description)
    # dataset = dataset.map(_create_description)
    dataset = dataset.map(_transform_key_meta)
    dataset = dataset.map(_create_full_json_answer)
    dataset = dataset.map(
        _create_prompt, fn_kwargs={"prompt_instruction": prompt_instruction_3}
    )
    dataset = dataset.map(_create_chat_data)
    dataset = cast_label(dataset)
    dataset = _drop_unused_data(dataset)
    for i, k in enumerate(dataset[0:2]):
        print(k, dataset[i][k])
    print_simple_info(dataset)

    # Save the dataset as an arrow file
    dataset.save_to_disk(training_set_path)


if __name__ == "__main__":
    main()
