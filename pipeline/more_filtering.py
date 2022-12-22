import pandas as pd
import argparse
from lxml import etree as ET
""" script to add more info """


def parse_xml(xmlString,id):
    document = ET.fromstring(xmlString)
    article_dict = {}
    for elementtag in document.getiterator():
        if elementtag.tag in ["year","aff","journal-id"]:
            article_dict[elementtag.tag] = elementtag.text

    return article_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script will add more data to the dataframe')
    parser.add_argument("-f", "--file", nargs=1, required=True, help="Input csv", metavar="PATH")
    parser.add_argument("-d", "--directory", nargs=1, required=True, help="Directory in which xml files are stored", metavar="PATH")
    
    args = parser.parse_args()
    file = args.file[0]
    directory = args.directory[0]
    df = pd.read_csv(file, header=None)
    dic_of_dicts = []

    for pmcid in df[0]:
    #     print(idx)
        filename=str(pmcid)+".xml"

        with open(directory +filename,"r") as xml:
                s_xml = xml.read()
                article_d = parse_xml(s_xml,id)
        article_d.update(idx._asdict())
        article_d.pop("Index")
        print(article_d)
        dic_of_dicts.append(article_d)
    df_new = pd.DataFrame(dic_of_dicts)
    print(df_new)
    df_new.to_csv("new_data.csv")
