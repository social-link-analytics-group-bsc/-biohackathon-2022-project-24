from transformers import pipeline
from pprint import pprint
import csv
import argparse
import json
from tqdm import tqdm


def parsing_arguments(parser):
    parser.add_argument("--data", type=str, default='data/candidate_sentences_last.csv',
                        help='Sentences that might contain numbers.')
    parser.add_argument("--out", type=str, default='data/results.json',
                        help='File to save the output')
    parser.add_argument("--model", type=str, default='output/bert-base-uncased-en/sbe.py_8_0.00005_date_22-11-10_time_14-55-26',
                        help='Pretrained model to find the numbers')
    return parser


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)
    print('Loading the data...')
    with open(args.data , 'r') as file:
        content = csv.reader(file, quotechar='"')
        #next(content)
        data = list(content)

    results = {}
    print('Loading the model...')
    nlp = pipeline("ner", model=args.model, device=0) # if you are working locally, remove device=0
    for line in tqdm(data):
        annotations = nlp(line[1])
        print(annotations)
        try:
            results[line[0]]
        except KeyError:
            results[line[0]] = {'n_fem':[], 'n_male':[], 'perc_fem':[], 'perc_male':[], 'sample':[]}
        for annotation in annotations:
            results[line[0]][annotation["entity"]].append(annotation["word"])
        with open(args.out, "a") as f_h:
            json.dump(results[line[0]], f_h)

    # with open(args.out, 'w') as o:
    #     json.dump(results, o)

if __name__ == "__main__":
    main()
