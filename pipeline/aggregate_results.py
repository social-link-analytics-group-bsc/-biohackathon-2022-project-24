import sqlite3
import pandas as pd
import yaml
import sys
import os
from word2number import w2n
import tqdm
import re
import json

def process_list(input_list):
    result_list = []
    for item in input_list:
        # Clean strings of any values that are not numbers or letters
        cleaned_item = re.sub(r'[^a-zA-Z0-9]', '', item)
        # Try to convert the item to an integer
        try:
            number = int(cleaned_item)
            result_list.append(number)
        except ValueError:
            # If it's not a valid integer, try word2number
            try:
                number = w2n.word_to_num(cleaned_item)
                result_list.append(number)
            except ValueError:
                # If word2number also fails, discard the item
                pass

    return result_list

# Add new row to results  
def add_analysis_entry(conn, cur, pmcid, dict):

    SQL_QUERY = """INSERT INTO Results (pmcid, agg_sentence_index, agg_n_male, agg_n_fem, agg_perc_male, agg_perc_fem, agg_sample, 
                    clean_n_male, clean_n_fem, clean_perc_male, clean_perc_fem, clean_sample,
                    max_n_male, max_n_fem, max_perc_male, max_perc_fem, max_sample) VALUES  
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cur.execute(SQL_QUERY, tuple(dict.values()))
    conn.commit()

# Connect to the SQLite database
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
config_all = yaml.safe_load(open(config_path))
DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]
conn = sqlite3.connect(DB_FILE)
#conn = sqlite3.connect("../data/mounted_db/db_info_articles_test.sqlite3")
cur = conn.cursor()

# Create a new table with the same structure as the aggregated DataFrame
cur.execute(
        """CREATE TABLE IF NOT EXISTS "Analysis" (
                "pmcid"	TEXT NOT NULL,
                "agg_sentence_index"	BLOB,
                "agg_n_fem"	BLOB,
                "agg_n_male"	BLOB,
                "agg_perc_fem"	BLOB,
                "agg_perc_male"	BLOB,
                "agg_sample"	BLOB,
                "clean_n_fem"	BLOB,
                "clean_n_male"	BLOB,
                "clean_perc_fem"	BLOB,
                "clean_perc_male"	BLOB,
                "clean_sample"	BLOB,
                "max_n_fem"	INTEGER,
                "max_n_male"	INTEGER,
                "max_perc_fem"	INTEGER,
                "max_perc_male"	INTEGER,
                "max_sample"	INTEGER,
                PRIMARY KEY ("pmcid") REFERENCES sections("pmcid")
            )"""
        )
conn.commit()

SQL_QUERY = f"SELECT * FROM Results;"
cur.execute(SQL_QUERY)
rows = cur.fetchall()

prev_pmcid = None
dict = {'pmcid' : None, 'agg_sentence_index' : [],
        'agg_n_male' : [], 'agg_n_fem' : [], 'agg_perc_male' : [], 'agg_perc_fem' : [], 'agg_sample' : [],
        'clean_n_male' : [], 'clean_n_fem' : [], 'clean_perc_male' : [], 'clean_perc_fem' : [], 'clean_sample' : [], 
        'max_n_male' : [], 'max_n_fem' : [], 'max_perc_male' : [], 'max_perc_fem' : [], 'max_sample' : []}

for row in rows:
    pmcid = row['pmcid']

    if pmcid != prev_pmcid:
        # We now have an entry with lists of values per pmcid
        # Go through list entries of important values and clean lists
        dict['clean_n_male'] = process_list(dict['agg_n_male'])
        dict['clean_n_fem'] = process_list(dict['agg_n_fem'])
        dict['clean_perc_male'] = process_list(dict['agg_perc_male'])
        dict['clean_perc_fem'] = process_list(dict['agg_perc_fem'])
        dict['clean_sample'] = process_list(dict['agg_sample'])

        # With the cleaned lists, get the max values and add these to table
        dict['max_n_male'] = max(dict['clean_n_male'])
        dict['max_n_fem'] = max(dict['clean_n_fem'])
        dict['max_perc_male'] = max(dict['clean_perc_male'])
        dict['max_perc_fem'] = max(dict['clean_perc_fem'])
        dict['max_sample'] = max(dict['clean_sample'])

        # Add dictionary to Analaysis table in database
        dict['pmcid'] = prev_pmcid
        add_analysis_entry(conn, cur, dict)

        dict['pmcid'] = None
        for key in dict:
            if key != pmcid:
                dict[key] = []

    # Add entries to dictionary
    dict['agg_sentence_index'].append(row['sentence_index'])
    dict['agg_n_male'].append(row['n_male'])
    dict['agg_n_fem'].append(row['n_fem'])
    dict['agg_perc_male'].append(row['perc_male'])
    dict['agg_perc_fem'].append(row['perc_fem'])
    dict['agg_sample'].append(row['sample'])

    prev_pmcid = pmcid

# Final add entry to add last dictionary to Analysis table 
dict['pmcid'] = prev_pmcid
add_analysis_entry(conn, cur, dict)

SQL_QUERY = "SELECT * FROM Analysis LEFT JOIN article_metadata ON Analysis.pmcid = article_metadata.pmcid WHERE article_metadata.pmcid IS NOT NULL;"
cur.execute(SQL_QUERY)
rows = cur.fetchall()

# Get the column names
columns = [desc[0] for desc in cur.description]

# Convert rows to a list of dictionaries
result = [dict(zip(columns, row)) for row in rows]

# Write the result to a JSON file
json_file_path = 'analysis.json'
with open(json_file_path, 'w') as json_file:
    json.dump(result, json_file, indent=2)

# Close the cursor and database connection
cur.close()
conn.close()