from transformers import pipeline
from pprint import pprint
import csv
import argparse
import json

def parsing_arguments(parser):
    parser.add_argument("--data", type=str, default='data/candidate_sentences_last.csv',
                        help='Tasks to evaluate')
    parser.add_argument("--out", type=str, default='results.json',
                        help='Tasks to evaluate')
    parser.add_argument("--model", type=str, default='results.json',
                        help='Tasks to evaluate')
    return parser


def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.data , 'r') as file:
        content = csv.reader(file, quotechar='"')
        #next(content)
        data = list(content)

    results = {}
    nlp = pipeline("ner", model=args.model, device=0)
    for line in data:
        annotations = nlp(line[1])
        try:
            results[line[0]]
        except KeyError:
            results[line[0]] = {'female':[], 'male':[], 'female_percentage':[], 'male_percentage':[]}
        for annotation in annotations:
            #print(annotation["entity"], annotation["word"])
            if annotation["entity"] == "M-NUM":
                results[line[0]]['male'].append(annotation["word"])
            elif annotation["entity"] == "F-NUM":
                results[line[0]]['female'].append(annotation["word"])
            elif annotation["entity"] == "M-PER":
                results[line[0]]['male_percentage'].append(annotation["word"])
            elif annotation["entity"] == "F-PER":
                results[line[0]]['female_percentage'].append(annotation["word"])
        #print(line)

    with open(args.out, 'w') as o:
        json.dump(results, o)


if __name__ == "__main__":
    main()