from transformers import pipeline
from pprint import pprint
import csv
import argparse
import json
from tqdm import tqdm
import sqlite3
import sys
import os
import yaml


def parsing_arguments(parser):
    # parser.add_argument("--data", type=str, default='data/candidate_sentences_last.csv',
    #                     help='Sentences that might contain numbers.')
    parser.add_argument("--out", type=str, default='data/results.json',
                        help='File to save the output')
    parser.add_argument("--model", type=str, default='output/bert-base-uncased-en/sbe.py_8_0.00005_date_22-11-10_time_14-55-26',
                        help='Pretrained model to find the numbers')
    return parser

# Method for getting database entries that still need to be run through the model
def get_entries(conn):
    SQL_QUERY = 'SELECT Main.pmcid, Main.methods FROM Main LEFT JOIN Results ON Main.pmcid = Results.pmcid WHERE Results.pmcid IS NULL;'
    cur = conn.cursor()
    cur.execute(SQL_QUERY)
    return cur.fetchall()

# Create table to record model results in (pmcid, n_fem, n_male, per_fem, perc_male, sample)
def create_results_table(conn):
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS "Results" (
                "pmcid"	TEXT NOT NULL,
                "n_fem"	TEXT,
                "n_male"	TEXT,
                "perc_fem"	TEXT,
                "perc_male"	TEXT,
                "sample"	TEXT,
                PRIMARY KEY("pmcid"),
                FOREIGN KEY ("pmcid") REFERENCES Main("pmcid")
            )"""
        )
    conn.commit()

# Add new row to results table
def add_result(conn, values):
    SQL_QUERY = "INSERT INTO Results (pmcid, n_male, n_fem, perc_male, perc_fem, sample) VALUES (?, ?, ?, ?, ?, ?)"
    cur = conn.cursor()
    cur.execute(SQL_QUERY, values)
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)
    print('Loading the data...')

    config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
    config_all = yaml.safe_load(open(config_path))

    # Connect to the SQLite database
    DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]
    conn = sqlite3.connect(DB_FILE)

    # Create results table (if not already created)
    create_results_table(conn)

    # Get entries from db that need to be run through the model
    entries = get_entries(conn)

    # Run entries through the model (sentence by sentence? check this)
    #nlp = pipeline("ner", model=args.model, device=0)
    nlp = pipeline("ner", model=args.model) # if you are working locally, remove device=0
    for row in entries:
        pmcid, methods = row
        annotations = nlp(methods)
        dict = {'n_male' : '', 'n_fem' : '', 'perc_male' : '', 'perc_fem' : '', 'sample' : ''}
        for annotation in annotations:
            dict[annotation["entity"]] = json.dumps(annotation["word"])

        # get values to be added to the db 
        values = list(dict.values())
        values.insert(0,pmcid)
        add_result(conn, values)

    conn.close()


if __name__ == "__main__":
    main()