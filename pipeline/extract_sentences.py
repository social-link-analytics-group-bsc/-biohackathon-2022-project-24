import os
import yaml
from nltk.tokenize import sent_tokenize, word_tokenize
# nltk.download('punkt') # uncomment the first time you run the script
import csv
from pathlib import Path
from tqdm import tqdm
from utils.extract_info import get_content

config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def find_candidate_sentences(text, relevant_tokens, get_null_sentences=False):
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
        if candidate and len(sent) < 300:
            interest_sentences.append(sent)

    if get_null_sentences:  # get also those IDs where there is no match
        if len(interest_sentences) == 0:
            interest_sentences = " "

    return interest_sentences


def main():
    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
    sentence_file_location = config_all['processing_params']['sentence_location']
    interesting_tokens = config_all['processing_params']['token_sentences']

    interesting_fields = ['METHODS', 'SUBJECTS']

    header = ["PMCID", "tokenized_text"]

    open(sentence_file_location, 'w')

    entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))
    count_articles = 0
    ext_sent = 0

    for file_ in tqdm(entire_files_to_parse):
        pmcid = file_.stem
        method_text = get_content(
            file_, interesting_fields, article_type='research-article')

        if method_text:
            count_articles += 1
            sentences = find_candidate_sentences(
                method_text, interesting_tokens, get_null_sentences=True)
            if sentences:
                ext_sent += 1

                with open(sentence_file_location, 'a') as o:
                    writer = csv.writer(o)
                    if count_articles == 1:
                        writer.writerow(header)
                    for sentence in sentences:
                        writer.writerow([pmcid, sentence])
                        # writer.writerow([pmcid, sentence, "None"])
                o.close()
    print(
        f'total of article with methods and subject extracted: {count_articles}')
    print(f'total of article with extracted sentences: {ext_sent}')


if __name__ == "__main__":
    main()
