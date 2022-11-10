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
    if annotation == 'NA':
        return '', ''
    percentage = False
    if '%' in annotation:
        percentage = True
        annotation = annotation.replace('%', '')
        #print(annotation)
    for i,token in enumerate(text):
        if token == annotation:
            print(token, annotation)
            return i, percentage
    return '',''

def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.data, 'r') as file:
        content = csv.reader(file, quotechar='"')
        data = list(content)
    print(len(data))

    with open('../data/original_sentences.csv', 'r') as file:
        content = csv.reader(file, quotechar='"')
        next(content)
        original = list(content)
        original_dict = {}
        for line in original:
            original_dict[line[0]+line[1]] = line[2]

    with open(args.out, 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        counts = 0
        for line in data:
            if line[1] != '':
                #counts += 1
                print(line)
                text = original_dict[line[0]]
                print(text)
                tokenized = word_tokenize(text)
                position_f, percentage = find_number(tokenized, line[1])
                position_m, percentage = find_number(tokenized, line[2])
                if position_f != '' or position_m != '':
                    print(position_m, position_f)
                    counts += 1
                for i, token in enumerate(tokenized):
                    if i == position_f:
                        if percentage:
                            writer.writerow([token, 'F-PER'])
                        writer.writerow([token, 'F-NUM'])
                    elif i == position_m:
                        if percentage:
                            writer.writerow([token, 'M-PER'])
                        writer.writerow([token, 'M-NUM'])
                    else:
                        writer.writerow([token, 'O'])
                writer.writerow([])
        print(counts)



if __name__ == "__main__":
    main()