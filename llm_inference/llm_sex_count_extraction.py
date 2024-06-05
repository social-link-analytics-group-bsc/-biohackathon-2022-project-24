import duckdb
import sys
import os
import yaml
import logging
import json
from tqdm import tqdm
from utils.prompt_instructions import prompt_instruction_3 as prompt_instruction
from llm_inference import LLMHandler, LLMHandlerInstruct


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


def validate_response(response, schema=None):
    # FIXME to implement a validation of the answer as json format against a schema
    # if json_validate:
    #     return response
    # else:
    #     return {'response': 'Wrong JSON'}
    return response


def recording_json_to_db(conn, json_response):
    # Record the json into a new table and add in the status the state of recording
    pass


def get_text_from_db(conn, table_sections):
    """
    Get the already recorded pmcids from db
    """
    # Execute a SELECT query to retrieve the pmcid values
    # Fetch rows with subjects or methods
    cursor = conn.cursor()
    cursor.execute(f"SELECT SUBJECTS, METHODS FROM {table_sections} WHERE METHODS IS NOT NULL OR SUBJECTS IS NOT NULL")
    row = cursor.fetchone()
    # Yield data if either subjects or methods are present
    # FIXME Not working still return if None in the methods
    while row:
        if row[0]:
            yield row[0]  # Yield subjects
        elif row[1]:
            yield row[1]  # Yield methods
        else:
            yield None
        row = cursor.fetchone()
    # Close the cursor and connection
    cursor.close()
    conn.close()

def get_text_from_dataset(file_path):
    pass


def main():

    # Load the config path
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    # DB connection
    # # Name of the database
    DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]
    table_status = config_all["db_params"]["table_status"]
    table_sections = config_all["db_params"]["table_sections"]
    table_metadata = config_all["db_params"]["table_metadata"]
    # # Using duckdb to access the sqlite file for compatibility on marenostrum
    conn = duckdb.connect(DB_FILE)

    # LLM setting
    model_outdir = config_all['llm_params']['model_outdir']
    model_name = config_all["llm_params"]["model_name"]
    model_path = f"{model_outdir}/{model_name}"
    instruct_model = config_all["llm_params"]['instruct_model']
    # get the adapter
    try:
        adapter_name = config_all["llm_params"]["adapter"]
        adapter_path = f"{model_outdir}/{adapter_name}"
    except KeyError:
        adapter_path = None
    generation_params = config_all["llm_params"]["generation_params"]
    # Load bitsandBytes config
    try:
        bits_and_bytes_config = config_all["llm_params"]["bits_and_bytes_config"]

    except KeyError:
        bits_and_bytes_config = None
    # Instantiate the model
    if instruct_model:
        llm_model = LLMHandlerInstruct(model_path, generation_params, prompt_instruction, bits_and_bytes_config, adapter_path=adapter_path)
    else:
        llm_model = LLMHandler(model_path, generation_params, prompt_instruction, bits_and_bytes_config, adapter_path=adapter_path)


    # Parsing the articles
    n=0
    for methods in get_text_from_db(conn, table_sections):
        prompt, answer = llm_model.passing_article_to_llm(methods)
        # print('PROMPT:\n')
        # print(prompt)
        print("ANSWER:\n")
        print(answer)
        n+=1
        if n == 10:
            raise


if __name__ == "__main__":
    main()
