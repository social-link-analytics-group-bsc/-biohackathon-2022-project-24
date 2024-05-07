# To transform the json into the meaninful json answer to train the model.
# Based on Blanca Calvo script and adapted
import argparse
import json
from datasets import load_dataset, Dataset


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
                    value = example["tokens"][span["token_start"]]["id"]
                    token_to_label.setdefault(label, []).append(value)
    except KeyError:  # if there are no spans
        token_to_label = {}
    example["labels"] = token_to_label
    return example


def _check_amount_counts(counts):
    if counts["n_male"] + counts["n_fem"] > counts["sample"]:
        return "Confusing information"
    elif counts["n_male"] > counts["sample"]:
        return "Confusing information"
    elif counts["n_fem"] > counts["sample"]:
        return "Confusing information"
    elif counts["perc_male"] + counts["perc_fem"] > 100:
        return "Confusing information"
    else:
        return "Correct information"


def _create_description(example):
    """
    Parse the example and transform the type of answer to a text
    The different answers are:
        - 'accept': All information is clear and about human subject
        - 'ignore': This is not about human subjects
        - 'reject': There is some confusing information
    """
    if example["answer"] == "accept":
        example["reason"] = "the article is about human subjects and the information is clear"
    elif example["answer"] == "reject":
        example["reason"] = (
            "The article is not about human subjects or contains more than just human subjects"
        )
    elif example["answer"] == "ignore":
        example["reason"] = (
            "The article is about human subject but some information are confusing"
        )
    return example


def _transform_key_meta(example):
    """
    Rename the embedded key meta.pmcid to pmcid
    """
    example["pmcid"] = example["meta"]["pmcid"]
    return example


def _create_full_json_answer(example):
    """
    Create the final answer for the model training.
    No more information is used for the training
    """
    example['full_answer'] = {'reason': example['reason'], 'labels': example['labels']}
    return example


def _drop_unused_data(dataset: Dataset) -> Dataset:
    """
    Use the built-in function for dropping columns.
    Need the dataset and not an example here
    Dropping all the columns except:
    - full_answer: answer for the model
    - pmcid: pmcid to be able to match the article
    - text: needed to generate the prompt
    - _annotator_id: The annotator in case random on that is important
    """
    col_to_drop = [
        "answer",
        "reason",
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


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()

    dataset = load_dataset("json", data_files=args.data, split="train")
    # print(dataset)
    dataset = dataset.map(_extract_labels)
    dataset = dataset.map(_create_description)
    dataset = dataset.map(_transform_key_meta)
    dataset = dataset.map(_create_full_json_answer)
    dataset = _drop_unused_data(dataset)

    # Save the dataset as an arrow file
    dataset.save_to_disk('final_dataset.hf')


if __name__ == "__main__":
    main()
