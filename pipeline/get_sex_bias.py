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
            with open('./output/start_index.txt', 'r') as file:
                start_index = int(file.read())
        except FileNotFoundError:
            start_index = 0
        except ValueError:
            start_index = 0

        print('Loading the model...')
        #nlp = pipeline("ner", model=args.model, device=0)
        nlp = pipeline("ner", model=args.model) # if you are working locally, remove device=0

        count = 0
        prev_id = None
        curr_id = None
        results = {}
        iterator = iter(list(content)[start_index:])

        # While loop working here depends on input file being sorted by PMCID such that
        # multiple entries pertaining to the same PMCID are consecutive in the file
        progress_bar = tqdm(total=len(list(content)) - start_index, desc="Processing Lines", dynamic_ncols=True)
        while True:
            try:
                line = next(iterator)
                annotations = nlp(line[1])
                curr_id = line[0]
                if curr_id == prev_id:
                    # add to existing entry
                    for annotation in annotations:
                        results[annotation["entity"]].append(annotation["word"])
                else:
                    # save current entry to json file
                    if results:
                        with open(args.out, "a") as f_h:
                            json.dump(results, f_h)
                            count += 1
                    # create new results entry 
                    results = {'n_fem':[], 'n_male':[], 'perc_fem':[], 'perc_male':[], 'sample':[]}
                    for annotation in annotations:
                        results[annotation["entity"]].append(annotation["word"])
                    # set prev_id to curr_id
                    prev_id = curr_id
                # Record index
                start_index += 1
                with open('./output/start_index.txt', 'w') as file:
                    file.write(str(start_index))
                progress_bar.update(1)
            except StopIteration:
                break  # Exit the loop when there are no more items
        
        print(f"The number of entries in output file '{args.out}' is: {count}")


if __name__ == "__main__":
    main()