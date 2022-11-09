import json
import pathlib
from nltk.tokenize import sent_tokenize, word_tokenize
import csv
import os
import yaml
config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def find_candidate_sentences(text, relevant_tokens):
    sentences = sent_tokenize((text))
    interest_sentences = []
    for sent in sentences:
        candidate = False
        window = 3
        tokenized = word_tokenize(sent)
        for i, token in enumerate(tokenized):
            if token.lower() in relevant_tokens:
                try:
                    check_tokens = tokenized[i-window:i+window]
                except IndexError:
                    try:
                        check_tokens = tokenized[i-1:i+1]
                    except IndexError:
                        continue
                for t in check_tokens:
                    if t.isnumeric():
                        candidate = True
        if candidate and len(sent) < 300:
            interest_sentences.append(sent)
    return interest_sentences


def main():

    dl_archive = config_all['search_params']['dl_archive']
    article_query_folder = config_all['api_europepmc_params']['article_query_folder']

    article_archive_folder = config_all['api_europepmc_params']['article_archive_folder']
    candidate_sentences = config_all['processing_params']['candidate_sentence_location']

    if dl_archive is True:
        article_folder = article_archive_folder
    else:
        article_folder = article_query_folder
    count_articles = 0
    interesting_tokens = ['man', 'woman', 'male',
                          'female', 'men', 'women', 'males', 'females']
    list_of_parse_article = list()
    with open(candidate_sentences, 'r') as f:
        spamreader = csv.reader(f, delimiter=',')
        for row in spamreader:
            list_of_parse_article.append(row[0])
            # print(', '.join(row))
    list_of_parse_article = set(list_of_parse_article)
    for article in pathlib.Path(article_folder).glob('*.jsonl'):
        pmcid = article.stem
        if pmcid not in list_of_parse_article:
            with open(article, 'r') as o:
                data = json.load(o)
            count_articles += 1

            sentences = find_candidate_sentences(data['METHODS'], interesting_tokens)

            with open(candidate_sentences, 'a') as o:
                for sentence in sentences:
                    print(sentence)
                    write = csv.writer(o)
                    write.writerow([pmcid, sentence])


if __name__ == "__main__":
    main()
