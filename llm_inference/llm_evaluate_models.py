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
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


def return_eval_score(evaluator, ref_json, pred_json):
    score = evaluator.evaluate_strings(prediction=pred_json, reference=ref_json)
    return score


def main():

    # Load the config path
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    # LLM setting
    model_path = config_all["llm_params"]["model"]
    type_instruct = config_all["llm_params"]["instruct_model"]
    generation_params = config_all["llm_params"]["generation_params"]

    # Instantiate the model
    if type_instruct is True:
        llm_model = LLMHandlerInstruct(model_path, generation_params)
    else:
        llm_model = LLMHandler(model_path, generation_params)

    # Instanciate the evaluation. Using Distance to provide a score of distance
    evaluator = JsonEditDistanceEvaluator()

    # Load the data from the model prediction
    training_set_path = config_all["llm_params"]["training_set_path"]
    data_loaded = datasets.load_from_disk(training_set_path)

    # Initialize a dictionary to store scores by answer type
    scores_by_answer_type = defaultdict(list)

    # Loop and pass it through the data and eval each answer
    for data in data_loaded:
        answer_training = data["answer_training"]
        answer_type = data["answer"]
        ref_json = answer_training
        prompt_instruction = data["prompt_instruction"]
        pmcid = data["pmcid"]
        method_text = data["text"][0:100]
        full_res = llm_model.passing_article_to_llm(
            prompt_instruction=prompt_instruction, text=method_text
        )
        print(full_res)
        raise
        # print(f"Pred Json: {pred_json}, {type(pred_json)}")
        # print(f"Ref Json: {ref_json}, {type(ref_json)}")
        # ref_json = ast.literal_eval(json.dumps(ref_json))
        # pred_json = ast.literal_eval(json.dumps(pred_json))
        # score = return_eval_score(evaluator, ref_json, pred_json)
        # scores_by_answer_type[answer_type].append(score)
        # print(f"{pmcid}: {answer_type}: {score}")

    # # Calculate overall average score
    # total_scores = [
        # score for scores in scores_by_answer_type.values() for score in scores
    # ]
    # overall_average_score = sum(total_scores) / len(total_scores)

    # # Calculate average score by answer type
    # average_score_by_answer_type = {
        # answer_type: sum(scores) / len(scores)
        # for answer_type, scores in scores_by_answer_type.items()
    # }

    # print(f"Overall average score: {overall_average_score}")
    # print("Average score by answer type:")
    # for answer_type, avg_score in average_score_by_answer_type.items():
        # print(f"{answer_type}: {avg_score}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
