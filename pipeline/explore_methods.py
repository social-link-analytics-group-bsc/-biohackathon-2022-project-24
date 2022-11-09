import json
import glob
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
#nltk.download('punkt') # uncomment the first time you run the script
import csv
import os

def find_candidate_sentences(text, relevant_tokens):
    sentences = sent_tokenize((text))
    interest_sentences = []
    for sent in sentences:
        candidate = False
        window = 3
        tokenized = word_tokenize(sent)
        for i,token in enumerate(tokenized):
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

    count_articles = 0
    interesting_tokens = ['man', 'woman', 'male', 'female', 'men', 'women', 'males', 'females']
    open('data/candidate_sentences.csv', 'w')

    for file in glob.glob("data/clean_articles/"+"*.jsonl"):
        print(file)
        with open(file, 'r') as o:
            data = json.load(o)
        count_articles += 1

        #text = data['METHODS']
        sentences = find_candidate_sentences(data['METHODS'], interesting_tokens)

        with open('data/candidate_sentences.csv', 'a') as o:
            for sentence in sentences:
                write = csv.writer(o)
                write.writerow([os.path.basename(file[:-6]), sentence])

if __name__ == "__main__":
    main()