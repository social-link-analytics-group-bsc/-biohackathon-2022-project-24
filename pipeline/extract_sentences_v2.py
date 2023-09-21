import os, sys
import yaml
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt') # uncomment the first time you run the script
import csv
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import numpy as np
import multiprocessing as mp 
from multiprocessing import  Pool
from ast import literal_eval

config_path = os.path.join(os.path.dirname(
    __file__), './config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

def add_features(df):
    interesting_tokens = config_all['processing_params']['token_sentences']
    df["methods"] = df.apply(lambda sentence: find_candidate_sentences(sentence, interesting_tokens, get_null_sentences=False) if sentence is not None else np.NaN, axis=1)
    return df 

def parallelize_dataframe(df, func, n_cores=mp.cpu_count()):
    df_split = np.array_split(df, n_cores, axis=0)
    pool = Pool(100)

    print(func, len(df_split))

    df = pd.concat(pool.map(func, df_split), axis=0)
    pool.close()
    pool.join()
    return df
    


def find_candidate_sentences(text, relevant_tokens, get_null_sentences=True):

    text = text.tolist()[1] # we need to convert a pd.Series object to retrieve the actual methods
    sentences = sent_tokenize((text))
    interest_sentences = []
    # token_found = set()
    for sent in sentences:
        candidate = False
        window = 3
        tokenized = word_tokenize(sent)
        for i, token in enumerate(tokenized):
            if token.lower().strip() in relevant_tokens:
                check_tokens = tokenized[i - window:i + window]
                for t in check_tokens:
                    if t.isnumeric():
                        candidate = True
        if candidate and len(sent) < 300 : #and len(sent) < 300 
            interest_sentences.append(sent)


    if get_null_sentences:  # get also those IDs where there is no match
        if len(interest_sentences) == 0:
            interest_sentences = " "

    return interest_sentences



def parallel_extract_sentences(input_csv, interesting_tokens,output_folder = f"{os.getcwd()}/data"):
    " "

    print("extracting tokenized sentences...")

    sentences_df = input_csv
    sentences_df = sentences_df.replace(r'\n','', regex=True) 

    tmp_df = sentences_df.copy()
    tmp_parallel_df = parallelize_dataframe(tmp_df, add_features)
    # tmp_parallel_df.to_csv(f"./output/parallel_470k_tokens_1207.csv", sep=',', encoding='utf-8', index=False)

    return tmp_parallel_df



def main():
    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
    out_sentences_location = config_all['processing_params']['tokenized_sentence_location']
    input_sentences_location = config_all['processing_params']['input_sentence_location']
    interesting_tokens = config_all['processing_params']['token_sentences']
    interesting_fields = ['METHODS']
    header = ["PMCID", "tokenized_text"]
    input_sentences_df = pd.read_csv(input_sentences_location, nrows=3000)
    out_parallel_sentences = parallel_extract_sentences(input_sentences_df, interesting_tokens)

    # explode the methods (first cast to list)
    out_parallel_sentences['methods'] = out_parallel_sentences['methods'].fillna({i: [] for i in out_parallel_sentences.index})
    out_parallel_sentences['methods'] = '[' + out_parallel_sentences['methods'].astype(str) + ']'
    out_parallel_sentences['methods'] = out_parallel_sentences['methods'].apply(literal_eval) #convert to list type

    # explode twice bc there are nested lists
    out_parallel_sentences = out_parallel_sentences.explode("methods")
    out_parallel_sentences = out_parallel_sentences.explode("methods")
    out_parallel_sentences = out_parallel_sentences.explode("methods")


    out_parallel_sentences.to_csv(out_sentences_location, header=True, index=False, sep=',', encoding='utf-8')




    

if __name__ == "__main__":
    main()
