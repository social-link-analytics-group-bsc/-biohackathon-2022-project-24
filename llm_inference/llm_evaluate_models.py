import os
import ast
import sys
import yaml
import json
import logging
from langchain.evaluation import JsonEditDistanceEvaluator
import datasets
from datasets import DatasetDict
from llm_inference import LLMHandler, LLMHandlerInstruct
from utils.prompt_instructions import prompt_instruction_3 as prompt_instruction
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


def return_eval_score(evaluator, ref_json, answer):

    ref_json = json.dumps(ref_json)
    pred_json = json.dumps(answer)
    # try:
    #   pred_json = json.loads(pred_json)
    # except (SyntaxError, NameError):
    #   print("Error: Invalid string format")
    #   return 0
    # try:
    #     del pred_json['sentence_where_found']
    # except KeyError:
    #     return 0
    # pred_json = json.dumps(pred_json)
    score = evaluator.evaluate_strings(prediction=pred_json, reference=ref_json)
    return score['score']


def main():

    # Load the config path
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    logger.info("Load the data for evaluation")
    # Load the data from the model prediction
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


    data_loaded = training_set['test']
    logger.info(f"Data loadaed:\n{data_loaded}")



    # LLM setting
    model_outdir = config_all['llm_params']['model_outdir']
    model_name = config_all["llm_params"]['inference']["model_name"]
    model_path = f"{model_outdir}{model_name}"
    instruct_model = config_all["llm_params"]['inference']['instruct_model']
    # Get the adapter
    generation_params = config_all["llm_params"]['inference']["generation_params"]
    # Load bitsandBytes config
    try:
        bits_and_bytes_config = config_all["llm_params"]['inference']["bits_and_bytes_config"]
    except KeyError:
        bits_and_bytes_config = None

    adapter = config_all['llm_params']['inference']['adapter']
    if adapter['loading'] is True:
        if adapter['quantization'] is not False:
            adapter_path = f"{model_outdir}{model_name}_lora_{adapter['quantization']}"
        else:
            adapter_path = f"{model_outdir}{model_name}_lora"
    else:
        adapter_path = None

    # Instantiate the model
    logger.info('Load the model in the GPU(s)')
    if instruct_model:
        llm_model = LLMHandlerInstruct(model_path, generation_params, bits_and_bytes_config=bits_and_bytes_config, adapter_path=adapter_path)
    else:
        llm_model = LLMHandler(model_path, generation_params,  bits_and_bytes_config=bits_and_bytes_config, adapter_path=adapter_path)
    logger.info("Model loaded")

    # Instanciate the evaluation. Using Distance to provide a score of distance
    evaluator = JsonEditDistanceEvaluator()

    # Initialize a dictionary to store scores by answer type
    scores_by_answer_type = dict()

    # Loop and pass it through the data and eval each answer
    n =0
    for data in data_loaded:
        answer_training = data["answer_training"]
        answer_type = data["answer"]
        if answer_type == 0:
            answer_type = "accept"
        elif answer_type == 1:
            answer_type = "reject"
        elif answer_type == 2:
            answer_type = "ignore"
        else:
            pass
        ref_json = answer_training
        # prompt_instruction = data["prompt_instruction"]
        pmcid = data["pmcid"]
        method_text = data["text"][0:100]
        answer = llm_model.passing_article_to_llm(
            prompt_instruction=prompt_instruction, text=method_text
        )
        # print(f"Pred Json: {pred_json}, {type(pred_json)}")
        # print(f"Ref Json: {ref_json}, {type(ref_json)}")
        score = return_eval_score(evaluator, ref_json, answer)
        scores_by_answer_type.setdefault(answer_type, []).append(score)
        print(f"{pmcid}: {answer_type}: {score}")
        n+=1
        if n >2:
            pass

    # Calculate overall average score
    total_scores = [score for value in scores_by_answer_type.values() for score in value]
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
    if adapter_path is not None:


if __name__ == "__main__":
    main()
