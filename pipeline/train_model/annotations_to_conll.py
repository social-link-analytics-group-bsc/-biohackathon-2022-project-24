import csv
import argparse
from nltk.tokenize import word_tokenize

def parsing_arguments(parser):
    parser.add_argument("--data", type=str, default='trial.csv',
                        help='Tasks to evaluate')
    parser.add_argument("--out", type=str, default='trial.conll',
                        help='Tasks to evaluate')
    return parser

def find_number(text, annotation):
    for i,token in enumerate(text):
        if token == annotation:
            return i

def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.data , 'r') as file:
        content = csv.reader(file, quotechar='"')
        data = list(content)

    with open(args.out, 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for line in data:
            tokenized = word_tokenize(line[1])
            position_f = find_number(tokenized, line[2])
            position_m = find_number(tokenized, line[3])
            for i, token in enumerate(tokenized):
                if i == position_f:
                    writer.writerow([token, 'F-NUM'])
                elif i == position_m:
                    writer.writerow([token, 'M-NUM'])
                else:
                    writer.writerow([token, 'O'])
            writer.writerow([])




if __name__ == "__main__":
    main()