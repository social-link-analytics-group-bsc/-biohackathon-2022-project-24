
import json
import glob

def main():
    count_articles = 0
    count_keyresource = 0
    for file in glob.glob("data/clean_articles/"+"*.jsonl"):
        with open(file, 'r') as o:
            data = json.load(o)
        count_articles += 1
        #print(data['TABLE'])
        for value in data['TABLE']:
            #if value == 'keyresource':
            count_keyresource += 1
            for line in data['TABLE'][value]:
                print(line)
        #if count_keyresource > 20:
        #    exit()

        print('{}/{}'.format(count_keyresource, count_articles))

if __name__ == "__main__":
    main()