import requests
from requests.exceptions import HTTPError

import xml.etree.ElementTree as ET
import logging
import os
import yaml
import sys

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


def apiSearch(pmcid, root_url):
    req = f'{root_url}{pmcid}/fullTextXML'
    r = requests.get(req)
    if not r:
        return
    root = ET.fromstring(r.content)
    if not root.findall('body'):
        return
    return root

# load pmcid from csv file
def getPMCidList(file_location):
  with open(file_location, 'r') as f:
    for l in f:
      l_split = l.split(',')
      if len(l_split) > 1:
        field = l_split[1]
      else:
        field = l_split[0]
      pmcid = field.split(':')[1]
      yield pmcid.rstrip()
    


def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    api_root_archive = config_all['api_europepmc_params']['archive_api']['root_url']
    file_root_archive = config_all['api_europepmc_params']['archive_file']
    rerun_archive = config_all['api_europepmc_params']['rerun_archive']
    file_location = config_all['ids_file_location']
    #if rerun_archive is True:
     #   db_utils.drop_database()
    #db_utils.create_database()

    # Get the present pcmid in case rerun=false to avoir re-dl everything
    # already_dl_pcmid = [i for i in db_utils.retrieve_existing_record()]

    dummyCounter = 0
    # archive = get_archive(file_root_archive, api_root_archive, rerun_archive)

    for pmcid in getPMCidList(file_location):
        print(pmcid)
        dummyCounter += 1
        article = apiSearch(pmcid, api_root_article)
        try:
            tree = ET.ElementTree(article)
            with open('data/articles/'+pmcid+'.xml', 'wb') as f:
                tree.write(f)
        except AttributeError:
            print('no output')


if __name__ == "__main__":
    main()
