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


def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    api_root_archive = config_all['api_europepmc_params']['archive_api']['root_url']
    file_root_archive = config_all['api_europepmc_params']['archive_file']
    rerun_archive = config_all['api_europepmc_params']['rerun_archive']
    if rerun_archive is True:
        db_utils.drop_database()
    db_utils.create_database()

    # Get the present pcmid in case rerun=false to avoir re-dl everything
    already_dl_pcmid = [i['pmcid'] for i in db_utils.retrieve_existing_record()]
    print(f"Size of already pcmid: {len(already_dl_pcmid)}")

    dummyCounter = 0
    archive = get_archive(file_root_archive, api_root_archive, rerun_archive)
    list_pmcid = [pmcid for pmcid in archive if pmcid not in already_dl_pcmid]
    for pmcid in list_pmcid:
        dummyCounter += 1
        article = apiSearch(pmcid, api_root_article)
        if article:
            section = retrieveSections(article)
            meta_data = retrieveMetadata(article)
            sup_material = retrieveSupplementary(article)
            db_utils.commitToDatabase(
                pmcid, section, meta_data, sup_material)
        print(f"Done {dummyCounter}, remains {len(list_pmcid) - dummyCounter}")


if __name__ == "__main__":
    main()
