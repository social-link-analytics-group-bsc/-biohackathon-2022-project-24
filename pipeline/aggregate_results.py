import sqlite3
import pandas as pd
import yaml
import sys
import os
from word2number import w2n
import tqdm

def process_list(input_list):
    result_list = []
    for item in input_list:
        # Try to convert the item to an integer
        try:
            number = int(item)
            result_list.append(number)
        except ValueError:
            # If it's not a valid integer, try word2number
            try:
                number = w2n.word_to_num(item)
                result_list.append(number)
            except ValueError:
                # If word2number also fails, discard the item
                pass

    return result_list

# Connect to the SQLite database
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
config_all = yaml.safe_load(open(config_path))
DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]
conn = sqlite3.connect(DB_FILE)
#conn = sqlite3.connect("../data/mounted_db/db_info_articles_test.sqlite3")

# Query the data from the Results table
SQL_QUERY = "SELECT * FROM Results;"
df = pd.read_sql_query(SQL_QUERY, conn)
conn.close()

# Aggregate rows with the same unique_id and make columns lists
aggregated_df = df.groupby('pmcid').agg(lambda x: list(x)).reset_index()

pbar = tqdm(total=len(aggregated_df.columns))
# Create new columns with 'max_' prefix and set values to the max values in the lists
for column in aggregated_df.columns:
    if column != 'pmcid':
        clean_column_name = 'clean_' + column
        max_column_name = 'max_' + column
        aggregated_df[clean_column_name] = None
        aggregated_df[max_column_name] = None
        for index, value in aggregated_df[column].items():
            aggregated_df.at[index, clean_column_name] = process_list(value)
            aggregated_df.at[index, max_column_name] = aggregated_df[clean_column_name].apply(lambda x: max(x) if x else None)
    pbar.update(n=1)

conn = sqlite3.connect(DB_FILE)
aggregated_df.to_sql('Analysis', conn, index=False, if_exists='replace', index_label='pmcid')

query = "SELECT * FROM Results LEFT JOIN article_metadata ON Results.pmcid = article_metadata.pmcid WHERE article_metadata.pmcid IS NOT NULL;"
joined_df = pd.read_sql_query(query, conn)
conn.close()

# Export the final dataframe to a JSON and CSV file
json_file_path = 'aggregated_data.json'
joined_df.to_json(json_file_path, orient='records', lines=True)
csv_file_path = 'aggregated_data.csv'
joined_df.to_csv(csv_file_path)