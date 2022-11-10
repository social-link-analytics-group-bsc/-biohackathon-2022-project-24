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
        # print(annotation)
    for i, token in enumerate(text):
        if token.replace(',', '') == annotation:
            return i, percentage
    return '', ''

def write_conll(split, data, max=None):
    counts = 0
    with open(split, 'w') as o:
        writer = csv.writer(o, delimiter='\t')
        for i,line in enumerate(data):
            if line[3] != '':
                counts += 1
                tokenized = word_tokenize(line[2])
                position_f, percentage = find_number(tokenized, line[3])
                position_m, percentage = find_number(tokenized, line[4])
                for p, token in enumerate(tokenized):
                    if p == position_f:
                        if percentage:
                            writer.writerow([token, 'F-PER'])
                        else:
                            writer.writerow([token, 'F-NUM'])
                    elif p == position_m:
                        if percentage:
                            writer.writerow([token, 'M-PER'])
                        else:
                            writer.writerow([token, 'M-NUM'])
                    else:
                        writer.writerow([token, 'O'])
                writer.writerow([])
            if counts == max:
                print(split)
                print(i)
                return data[i:]
        return counts

def main():
    parser = argparse.ArgumentParser()
    parser = parsing_arguments(parser)
    args = parser.parse_args()
    print(args)

    with open(args.data , 'r') as file:
        content = csv.reader(file, quotechar='"')
        next(content)
        data = list(content)

    print(len(data))

    remaining_data = write_conll('train.conll', data, 500)
    print(len(remaining_data))
    remaining_data = write_conll('dev.conll', remaining_data, 100)
    print(len(remaining_data))
    remaining_data = write_conll('test.conll', remaining_data, 100)
    print(len(remaining_data))
    left = write_conll('remaining.conll', remaining_data)
    print('Not used', left)
    print('Total', 300+50+50+left)





if __name__ == "__main__":
    main()