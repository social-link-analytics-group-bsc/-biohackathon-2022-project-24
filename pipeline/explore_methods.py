import pandas as pd
from ast import Break
import json
import pathlib
from nltk.tokenize import sent_tokenize, word_tokenize
import csv
import os
import yaml
config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def find_candidate_sentences(text, relevant_tokens, get_null_sentences=False):
    sentences = sent_tokenize((text))
    interest_sentences = []
    for sent in sentences:
        candidate = False
        window = 3
        tokenized = word_tokenize(sent)
        for i, token in enumerate(tokenized):
            if token.lower() in relevant_tokens:
                check_tokens = tokenized[i-window:i+window]
                for t in check_tokens:
                    if t.isnumeric():
                        candidate = True
        if candidate and len(sent) < 300:
            interest_sentences.append(sent)

    if get_null_sentences:  # get also those IDs where there is no match
        if len(interest_sentences) == 0:
            return ["None"]  # convert to NaN at df level

    return interest_sentences


def main():

    dl_archive = config_all['search_params']['dl_archive']
    article_query_folder = config_all['api_europepmc_params']['article_query_folder']

    article_archive_folder = config_all['api_europepmc_params']['article_archive_folder']
    candidate_sentences_location = config_all['processing_params']['candidate_sentence_location']

    if dl_archive is True:
        article_folder = article_archive_folder
    else:
        article_folder = article_query_folder

    interesting_tokens = ['man', 'woman', 'male',
                          'female', 'men', 'women', 'males', 'females']
    header = ["PMCID", "tokenized_METHODS", "keywords"]

    open(candidate_sentences_location, 'w')

    for filename in pathlib.Path(article_folder).glob('*.jsonl'):
        pmcid = filename.stem
        with open(filename, 'r') as o:
            json_df = pd.read_json(filename)

        # filter JSON files that have no rows
        if json_df.empty:
            pass
        if json_df.shape[0] > 1:
            json_df_clean = json_df.loc[json_df.astype(
                str).drop_duplicates().index]
            json_df_clean = json_df_clean.iloc[0]  # this is just a workaround
            # json_df_clean.drop("TABLE", inplace=True)

        sentences = find_candidate_sentences(
            json_df["METHODS"], interesting_tokens, get_null_sentences=True)

        with open(candidate_sentences_location, 'a') as o:
            writer = csv.writer(o)
            writer.writerow(header)

            for sentence in sentences:
                try:  # Only when "full" df is used
                    writer.writerow(
                        [pmcid, sentence, json_df_clean["KEYWORDS"]])
                except:
                    writer.writerow([pmcid, sentence, "None"])
        o.close()


if __name__ == "__main__":
    main()
