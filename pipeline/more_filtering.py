import requests
from requests.exceptions import HTTPError
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

import logging
import os
import json
import yaml
from tqdm import tqdm
import pathlib
import urllib.parse

import pandas as pd
import argparse
from lxml import etree as ET
""" script to add more info """


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def parse_xml(xmlString,id):
    document = ET.fromstring(xmlString)
    article_dict = {}
    for elementtag in document.getiterator():
        if elementtag.tag in ["year","aff","journal-id"]:
            article_dict[elementtag.tag] = elementtag.text

    return article_dict

def get_request(url, params):
    try:
        response = requests.get(url, params)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        return response

'''
def getMetdata(pmcid, search_api_url, payload):
    pmcid = f'PMC:{pmcid[3:]}'
    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    result = get_request(search_api_url, params)
    result_json = result.json()
'''

def getAnnotations(pmcid, annotation_api_url, params):
    extra_params = {'articleIds': f'PMC:{pmcid[3:]}', 'format': 'XML'}
    new_p = dict(params)
    new_p.update(extra_params)
    result = get_request(annotation_api_url, new_p)
    root = ET.fromstring(result.content)
    return root

def retrieveAnnotations(pmcid, annotation_api_url, params):
    root = getAnnotations(pmcid, annotation_api_url, params)
    annot_dict = {'PMCID': pmcid}
    for k in params.keys():
        l = []
        for a in root.iter('annotation'):
            if  a.find(k).text:
                l.append(a.find('exact').text)
        annot_dict[params[k]] = '|'.join(list(l))

    return annot_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script will add more data to the dataframe')
    parser.add_argument("-f", "--file", nargs=1, required=True, help="Input csv", metavar="PATH")
    parser.add_argument("-d", "--directory", nargs=1, required=True, help="Directory in which xml files are stored", metavar="PATH")
    parser.add_argument("-a", "--annotation", nargs=1, required=False, help="Directory in which xml files are stored", metavar="PATH")
    
    annotation_api = config_all['api_europepmc_params']['annotations_api']['root_url']
    params = {'type':'Diseases'}

    args = parser.parse_args()
    file = args.file[0]
    directory = args.directory[0]
    annotation = args.annotation[0]

    df = pd.read_csv(file)
    dic_of_dicts = []
    for idx in df.itertuples():
        id =idx.PMCID
        filename=str(idx.PMCID)+".xml"

        with open(directory +filename,"r") as xml:
                s_xml = xml.read()
                article_d = parse_xml(s_xml,id)
        article_d.update(idx._asdict())
        article_d.pop("Index")
        print(article_d)
        dic_of_dicts.append(article_d)

        if annotation == "Y":
            annotations = retrieveAnnotations(id, annotation_api, params)
            print(annotations)
            dic_of_dicts.append(annotations)

    df_new = pd.DataFrame(dic_of_dicts)
    print(df_new)
    df_new.to_csv("new_data.csv")
