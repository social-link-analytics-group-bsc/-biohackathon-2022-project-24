from ast import Break
import json
import glob
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
# nltk.download('punkt') # uncomment the first time you run the script
import csv
import os
import pandas as pd


def find_candidate_sentences(text, relevant_tokens, get_null_sentences=False):
    sentences = sent_tokenize((text))
    interest_sentences = []
    for sent in sentences:
        candidate = False
        window = 3
        tokenized = word_tokenize(sent)
        for i, token in enumerate(tokenized):
            if token.lower() in relevant_tokens:
                check_tokens = tokenized[i - window:i + window]
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
    count_articles = 0
    interesting_tokens = ['man', 'woman', 'male', 'female', 'men', 'women', 'males', 'females']
    header = ["PMCID", "tokenized_METHODS", "keywords"]

    open('data/candidate_sentences.csv', 'w')

    for file in glob.glob("data/clean_articles/" + "*.jsonl"):
        # print(file)
        with open(file, 'r') as o:
            data = json.load(o)
            json_df = pd.read_json(file)

        count_articles += 1

        # filter JSON files that have no rows
        if json_df.empty:
            pass
        if json_df.shape[0] > 1:
            json_df_clean = json_df.loc[json_df.astype(str).drop_duplicates().index]
            json_df_clean = json_df_clean.iloc[0]  # this is just a workaround
            # json_df_clean.drop("TABLE", inplace=True)

        sentences = find_candidate_sentences(data["METHODS"], interesting_tokens, get_null_sentences=True)

        with open('data/candidate_sentences.csv', 'a') as o:
            writer = csv.writer(o)
            if count_articles == 1:
                writer.writerow(header)

            for sentence in sentences:
                filename = os.path.basename(file[:-6]).split("archive_articles_tagged")[1]

                try:  # Only when "full" df is used
                    writer.writerow([filename, sentence, json_df_clean["KEYWORDS"]])
                except:
                    writer.writerow([filename, sentence, "None"])
    o.close()


if __name__ == "__main__":
    main()
