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
    print(params)
    result = get_request(annotation_api_url, params)
    root = ET.fromstring(result.content)
    return root

def retrieveAnnotations(pmcid, annotation_api_url, params):
    params = 'query={pmcid}&resultType=core&cursorMark=*&pageSize=25&format=xml'
    root = getAnnotations(pmcid, f'{annotation_api_url}search', params)
    meta_dict = {'PMCID': pmcid}
    l = []
    for m in root.iter('meshHeading'):
            l.append(m.find('descriptorName').text)
    meta_dict['MESH'] = '|'.join(list(l))

    return meta_dict



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script will add more data to the dataframe')
    parser.add_argument("-f", "--file", nargs=1, required=True, help="Input csv", metavar="PATH")
    #parser.add_argument("-d", "--directory", nargs=1, required=True, help="Directory in which xml files are stored", metavar="PATH")
    parser.add_argument("-m", "--meta", nargs=1, required=True, help="Directory in which xml files are stored", metavar="PATH")
    
    annotation_api = config_all['api_europepmc_params']['rest_articles']['root_url']

    args = parser.parse_args()
    file = args.file[0]
    meta = args.meta[0]

    df = pd.read_csv(file)

    annots = []

    for idx in df.itertuples():
        annotations = retrieveAnnotations(idx.PMCID, annotation_api, meta)
        annots.append(annotations)


    df_ann = pd.DataFrame(annots)

    print(df_ann)

    result = pd.merge(df.reset_index(drop=True), df_ann.reset_index(drop=True), on="PMCID", how="left")
    result.to_csv("new_data_with_mesh_terms.csv", index=False)
