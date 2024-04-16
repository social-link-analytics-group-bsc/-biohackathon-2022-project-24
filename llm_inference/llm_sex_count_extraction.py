import re
import duckdb
import sys
import os
import yaml
import logging
import random
import json
from tqdm import tqdm
from threading import Thread
from prompt_instructions import prompt_instruction
from llm_generate_response import LLMHandler

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
    cursor.execute(f"SELECT SUBJECTS, METHODS FROM {table_sections}")
    row = cursor.fetchone()
    # Yield data if either subjects or methods are present
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
    model_path = config_all["llm_params"]["model"]
    generation_params = config_all["llm_params"]["generation_params"]
    # Instantiate the model
    llm_model = LLMHandler(model_path, generation_params, prompt_instruction)

    # Parsing the articles
    for methods in get_text_from_db(conn, table_sections):
        prompt_context, answer = llm_model.passing_article_to_llm(methods)

        print(answer)


if __name__ == "__main__":
    main()
