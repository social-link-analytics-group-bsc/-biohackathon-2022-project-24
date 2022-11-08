import requests
from requests.exceptions import HTTPError

import xml.etree.ElementTree as ET
import sqlite3
import gzip
import io
import logging
import os
import yaml
import sys
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db_utils import db_utils

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


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
        return requests.get(url, params)


def retrieveSupplementary(root):
    for supplementary in root.iter('supplementary-material'):
        return str(ET.tostring(supplementary)).replace('"', "'")


def retrieveMetadata(root):
    dictMetadata = {
        'issn': {'ppub': '', 'epub': ''},
        'journalTitle': '',
        'publisherName': ''
    }
    for front in root.iter('front'):
        for journalId in front.iter('issn'):
            if "ppub" in journalId.attrib['pub-type']:
                dictMetadata['issn']['ppub'] = ''.join(journalId.itertext())
            if "epub" in journalId.attrib['pub-type']:
                dictMetadata['issn']['epub'] = ''.join(journalId.itertext())
        for journalTitle in front.iter('journal-title'):
            dictMetadata['journalTitle'] = ''.join(journalTitle.itertext())
        for publisher in front.iter('publisher-name'):
            dictMetadata['publisherName'] = ''.join(publisher.itertext())
    return dictMetadata


# Retrieve the text for each section
def retrieveSections(root):

    dictSection = {'Intro': '', 'Method': '', 'Result': '', 'Discussion': ''}
    for body in root.iter('body'):
        for child in body.iter('sec'):
            if "sec-type" in child.attrib:
                for section in dictSection.keys():  # For each section in dictSection
                    # Sections inside sec-type are written in the following form:
                    # intro, methods, results, discussion
                    if section.lower() in child.attrib["sec-type"].lower():
                        dictSection[section] = ''.join(child.itertext()).replace(
                            '"', "'")  # Text without tags
                        # dictSection[section] = ET.tostring(child) # Text with tags
            if child[0].text:
                for section, sectionData in dictSection.items():
                    if sectionData:
                        continue
                    if section.lower() in child[0].text.lower():
                        dictSection[section] = ''.join(child.itertext()).replace(
                            '"', "'")  # Text without tags
                        # dictSection[section] = ET.tostring(child) # Text with tags
    return dictSection


def get_archive(file_location, url, rerun=False):

    if rerun is False:
        try:
            open_f = open(file_location, 'rb')
            f = io.BytesIO(open_f.read())
        except FileNotFoundError:
            rerun = True
    if rerun is True:
        logger.info(f"Getting the archive at {url}")

        OAUrl = requests.get(url)
        gzFile = OAUrl.content
        location = open(file_location, 'wb')
        location.write(gzFile)
        f = io.BytesIO(gzFile)
        logger.info(f"Writing archive in {file_location}")
    with gzip.GzipFile(fileobj=f) as OAFiles:
        n=0
        for OAFile in OAFiles:
            yield str(OAFile[:-1], 'utf-8')
            n+=1
            if n == 100000:
                return


def apiSearch(query, root_url):
    req = f'{root_url}search/query={query}&resultType=idlist&cursorMark=*&pageSize=100'
    r = requests.get(req)
    if not r:
        return
    root = ET.fromstring(r.content)
    #if not root.findall('body'):
    #   return
    return root


def getNextPagesResults(root):
    nextpage = root.find('nextPageUrl')
    ids = []
    while not nextpage is None:
        r = requests.get(nextpage.text)
        root = ET.fromstring(r.content)
        pmcids = retrievePmcids(root)
        nextpage = root.find('nextPageUrl')
        ids = ids + pmcids
    return ids


def retrievePmcids(root):
    pmcids = []
    for e in root.iter('result'):
        if e.find('pmcid') != None:
            pmcids.append(e.find('pmcid').text)
    return pmcids

def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    file_name = config_all['search_params']['ids_file_location']
    query = config_all['search_params']['query']

    root = apiSearch(query, api_root_article)
    pmcids = retrievePmcids(root)
    ids = getNextPagesResults(root)

    try:
        with open(file_name, 'w') as f:
            for pmcid in pmcids:
                print(pmcid)
                f.write(pmcid)
    except AttributeError:
        print('no output')
    

if __name__ == "__main__":
    main()