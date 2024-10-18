import argparse
import datetime
import json
import logging
import os
import sys

import duckdb
from tqdm import tqdm
from utils.model_loader import ModelLoader
from utils.post_process_answer import format_answer
from utils.utils import dynamic_import, load_config

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def setup_logger() -> logging.Logger:
    """Setup the logger configuration for consistency."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


logger = setup_logger()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the script."""
    parser = argparse.ArgumentParser(description="Model Evaluation Script")

    parser.add_argument(
        "--model", required=True, type=str, help="Path or name of the model to load."
    )
    parser.add_argument(
        "--quantization", type=str, help="Quantization level for the model."
    )
    parser.add_argument(
        "--instruct",
        action="store_true",
        help="Flag indicating if the model is an instruct model.",
    )
    parser.add_argument(
        "--adapter",
        action="store_true",
        help="Flag to indicate if an adapter should be loaded.",
    )
    parser.add_argument(
        "--adapter_quantization",
        default=False,
        type=str,
        help="Specify if the adapter is quantized.",
    )
    parser.add_argument(
        "--prompt", required=True, type=str, help="Path to the prompt file."
    )
    parser.add_argument(
        "--chain_prompt",
        action="store_true",
        help="Flag indicating if it use chain prompt",
    )
    return parser.parse_args()


def get_matching_pmcid(conn, table_sections, table_status):
    """
    Get the pmcid list of matching research
    """
    cursor = conn.cursor()
    query = f"""
        SELECT PMCID
        FROM {table_status}
        WHERE SUBJECTS = 1 OR METHODS = 1
    """
    cursor.execute(query)
    pmcid = cursor.fetchall()
    pmcid_list = [row[0] for row in pmcid]
    cursor.close()
    return pmcid_list


def get_text_from_db(conn, table_sections, pmcid):
    """
    Get the already recorded pmcids from db
    """
    cursor = conn.cursor()
    query = f"""
        SELECT ABSTRACT, SUBJECTS, METHODS
        FROM {table_sections} 
        WHERE pmcid = ?
    """
    cursor.execute(query, (pmcid,))
    row = cursor.fetchone()
    cursor.close()
    if row:
        abstract, subjects, method = row
        return abstract, subjects, method
    else:
        return None, None, None


def insert_into_db(data, metadata, conn, table):
    cursor = conn.cursor()

    if data is None:
        # Insert default values if data is not validated
        cursor.execute(
            f"""
            INSERT INTO {table} (answer, sample_total, sample_sample, sample_sentence_where_found, 
                                 male_total, male_sample, male_sentence_where_found, 
                                 female_total, female_sample, female_sentence_where_found, 
                                 date, model, prompt, quantization, adapter, adapter_quantization, pmcid) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Not validated",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                metadata["date"],
                metadata["model"],
                metadata["prompt"],
                metadata["quantization"],
                metadata["adapter"],
                metadata["adapter_quantization"],
                metadata["pmcid"],
                metadata["chain_prompt"],
            ),
        )
    else:
        # Extract relevant information from the validated data
        answer = data.get("answer", None)
        labels = data.get("labels", {})

        sample = labels.get("sample", {})
        male = labels.get("male", {})
        female = labels.get("female", {})

        # Insert into the database with the validated data
        cursor.execute(
            f"""
            INSERT INTO {table} (answer, sample_total, sample_sample, sample_sentence_where_found, 
                                 male_total, male_sample, male_sentence_where_found, 
                                 female_total, female_sample, female_sentence_where_found, 
                                 date, model, prompt, quantization, adapter, adapter_quantization, pmcid) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                answer,
                sample.get("total", None),
                json.dumps(sample.get("sample", [])),
                json.dumps(sample.get("sentence_where_found", [])),
                male.get("total", None),
                json.dumps(male.get("sample", [])),
                json.dumps(male.get("sentence_where_found", [])),
                female.get("total", None),
                json.dumps(female.get("sample", [])),
                json.dumps(female.get("sentence_where_found", [])),
                metadata["date"],
                metadata["model"],
                metadata["prompt"],
                metadata["quantization"],
                metadata["adapter"],
                metadata["adapter_quantization"],
                metadata["pmcid"],
            ),
        )

    cursor.close()
    conn.commit()


def main():
    args = parse_arguments()
    logger.info(f"Arguments: {args}")

    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = load_config(config_path)
    logger.info(f"Using model: {args.model}")

    # DB connection
    # # Name of the database
    DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]
    table_status = config_all["db_params"]["table_status"]
    table_sections = config_all["db_params"]["table_sections"]
    table_metadata = config_all["db_params"]["table_metadata"]
    table_inference = config_all["db_params"]["table_inference"]
    # # Using duckdb to access the sqlite file for compatibility on marenostrum
    conn = duckdb.connect(DB_FILE)
    # TODO: refactor these keys with the other times I call the execute on this table in this code
    create_inference_sql = f"""CREATE TABLE IF NOT EXISTS {table_inference} ( answer VARCHAR,
    sample_total INTEGER,
    sample_sample VARCHAR,
    sample_sentence_where_found VARCHAR, 
    male_total INTEGER,
    male_sample VARCHAR,
    male_sentence_where_found VARCHAR,
    female_total INTEGER,
    female_sample VARCHAR,
    female_sentence_where_found VARCHAR,
    date TIMESTAMP,
    model VARCHAR,
    prompt VARCHAR,
    quantization VARCHAR,
    adapter VARCHAR,
    adapter_quantization VARCHAR,
    pmcid VARCHAR);"""
    c = conn.cursor()
    c.execute(create_inference_sql)
    conn.commit()

    # Initialize ModelLoader
    model_loader = ModelLoader(
        model_path=args.model,
        quantization=args.quantization,
        instruct=args.instruct,
        adapter=args.adapter,
        adapter_quantization=args.adapter_quantization,
        generation_params=config_all["llm_params"]["generation_params"],
        bits_and_bytes_config=config_all["llm_params"]["bits_and_bytes"],
    )
    # Load the model
    llm_model = model_loader.get_model()

    # Load prompt instruction
    prompt_instruction = dynamic_import(f"utils.{args.prompt}", "prompt_instruction")
    date = datetime.datetime.now().strftime("%d/%m/%Y")

    # Creating the metadata variable to be stored in the table alongside the results
    metadata = vars(args)
    # add the date to the metadata
    metadata["date"] = date
    # Parsing the articles
    pmcid_list = get_matching_pmcid(conn, table_sections, table_status)
    n = 0
    for pmcid in tqdm(pmcid_list):
        abstract, subject, method = get_text_from_db(conn, table_sections, pmcid)
        # Add the PMCID to the metadata
        metadata["pmcid"] = pmcid
        # if abstract:
        #     print(f"PMCID: {pmcid}, Abstract: {abstract}, Subjects: {subject}, Methods: {method}")
        # else:
        #     print(f"No data found for PMCID: {pmcid}")

        if method is not None:
            answer = llm_model.passing_article_to_llm(
                prompt_instruction=prompt_instruction,
                text=method,
            )
        else:
            print(pmcid)
            answer = None

        inference_full_answer = format_answer(answer)
        insert_into_db(
            data=inference_full_answer,
            metadata=metadata,
            conn=conn,
            table=table_inference,
        )
    #
    #     n += 1
    #     if n == 10:
    #         raise

if __name__ == "__main__":
    main()
