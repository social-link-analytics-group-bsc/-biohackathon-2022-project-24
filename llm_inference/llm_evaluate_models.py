import os
import argparse
import ast
import sys
import json
import logging
import datetime
from langchain.evaluation import JsonEditDistanceEvaluator
import datasets
from datasets import DatasetDict
from llm_inference import LLMHandler, LLMHandlerInstruct
from utils.prompt_instructions import prompt_instruction_3 as prompt_instruction
from utils.utils import (
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


def format_answer(answer):
    try:
        return ast.literal_eval(answer)
    except:
        print(answer)
        return {}


def clean_keys(answer, reference):
    """
    Checks recursively if the keys present in answer are also present in the
    ref dictionary. If not it just delete them
    """
    if not isinstance(reference, dict) or not isinstance(answer, dict):
        return answer
    pruned = {}
    for key in reference:
        if key in answer:
            if isinstance(reference[key], dict) and isinstance(answer[key], dict):
                pruned[key] = clean_keys(reference[key], answer[key])
            else:
                pruned[key] = answer[key]
    return pruned


def remove_none_values(d):
    """
    Remove all the None answer to avoid inflating the comparison when it does not provide any values
    """
    if not isinstance(d, dict):
        return d
    return {k: remove_none_values(v) for k, v in d.items() if v is not None}


def return_eval_score(evaluator, ref_json, pred_json):

    score = evaluator.evaluate_strings(prediction=pred_json, reference=ref_json)
    return score["score"]


def main():

    parser = argparse.ArgumentParser()
    parser = get_arguments(parser)
    args = parser.parse_args()
    logger.info(f"Using model: {args.model}")

    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = load_config(config_path)

    config_model_path = os.path.join(
        os.path.dirname(__file__), "../config", f"{args.model}.yaml"
    )
    config_model = load_config(config_model_path)

    model_path = setup_model_path(config_all, config_model)
    adapter_path, adapter_id = setup_adapter_path(model_path, config_model)

    model_quantization = config_model["inference"]["quantization"]
    model_quantization, bitsandbytes = setup_bits_and_bytes_config(
        model_quantization, config_model["bits_and_bytes"]
    )
    generation_params = config_model["inference"]["generation_params"]

    model_id = f"{model_path}_{model_quantization}{adapter_id}"

    logger.info("Load the model in the GPU(s)")
    if config_model["inference"]["instruct_model"]:
        llm_model = LLMHandlerInstruct(
            model_path,
            generation_params,
            bits_and_bytes_config=bitsandbytes,
            adapter_path=adapter_path,
        )
    else:
        llm_model = LLMHandler(
            model_path,
            generation_params,
            bits_and_bytes_config=bitsandbytes,
            adapter_path=adapter_path,
        )
    logger.info("Model loaded")

    ## Dataset
    logger.info("Load the data for evaluation")
    # Load the data from the model prediction
    eval_result_path = config_all["llm_params"]["eval_result_path"]
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

    data_loaded = training_set["test"]
    logger.info(f"Data loadaed:\n{data_loaded}")

    # Instanciate the evaluation. Using Distance to provide a score of distance
    evaluator = JsonEditDistanceEvaluator()

    # Initialize a dictionary to store scores by answer type
    scores_by_answer_type = dict()

    # Loop and pass it through the data and eval each answer
    n = 0
    for data in data_loaded:
        answer_training = data["answer_training"]
        answer_type = data["answer"]

        # prompt_instruction = data["prompt_instruction"]
        pmcid = data["pmcid"]
        method_text = data["text"][0:100]
        answer = llm_model.passing_article_to_llm(
            prompt_instruction=prompt_instruction, text=method_text
        )

        ref_json = format_answer(answer_training)
        print(f"Ref json: {ref_json} - Type: {type(ref_json)}")

        pred_json = format_answer(answer)
        print(f"pred json: {pred_json} - Type: {type(pred_json)}")

        cleaned_pred_json = clean_keys(reference=ref_json, answer=pred_json)

        cleaned_pred_json = remove_none_values(cleaned_pred_json)
        cleaned_ref_json = remove_none_values(ref_json)

        print(f"cleaned pred json: {cleaned_pred_json}")
        print(f"cleaned ref json: {cleaned_ref_json}")

        score = return_eval_score(evaluator, cleaned_ref_json, cleaned_pred_json)
        scores_by_answer_type.setdefault(answer_type, []).append(score)
        print(f"{pmcid}: {answer_type}: {score}")

        n += 1
        if n > 2:
            pass

    # Calculate overall average score
    total_scores = [
        score for value in scores_by_answer_type.values() for score in value
    ]
    overall_average_score = sum(total_scores) / len(total_scores)

    # Calculate average score by answer type
    average_score_by_answer_type = {
        answer_type: sum(scores) / len(scores)
        for answer_type, scores in scores_by_answer_type.items()
    }

    print(f"Overall average score: {overall_average_score}")
    print("Average score by answer type:")
    for answer_type, avg_score in average_score_by_answer_type.items():
        print(f"{answer_type}: {avg_score}")

    results = {
        "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "model_name": config_model["inference"]["model_name"],
        "model_quantization": model_quantization,
        "adapteur": config_model["inference"]["adapter"],
        "adapteur_quantization": config_model["peft"]["quantization"],
        "score_agg": overall_average_score,
        "score_0": average_score_by_answer_type.get(0, 0),
        "score_1": average_score_by_answer_type.get(1, 0),
        "score_2": average_score_by_answer_type.get(2, 0),
        "eval_size": len(total_scores),
    }

    with open(eval_result_path, "a") as result_file:
        json.dump(results, result_file, indent=2)


if __name__ == "__main__":
    main()
