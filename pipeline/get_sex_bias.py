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
        #data = list(content)

        # Check to see if there is an index of the results we should start at
        try:
            # Try to open the text file and read the starting index
            with open('start_index.txt', 'r') as file:
                start_index = int(file.read())
        except FileNotFoundError:
            start_index = 0
        except ValueError:
            start_index = 0

        results = {}
        print('Loading the model...')
        nlp = pipeline("ner", model=args.model, device=0) # if you are working locally, remove device=0
        for line in tqdm(list(content)[start_index:]):
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
            # Record index
            start_index += 1
            with open('start_index.txt', 'w') as file:
                file.write(str(start_index))
        
        # ISSUE with adding the json dump within the for loop is that if there are multiple results/
        # annotations/sentences for one pmcid, then they will each be written as separate 
        # entries in the json file, adding on the previous one each time so that the last
        # instance of a pmcid entry written in the json file is the most up to date.
        # We could use this to then write a quick script that only keeps the last entry of a
        # pmcid in the json file. Or is there a way to write directly to a previous entry
        # in a json file?

if __name__ == "__main__":
    main()