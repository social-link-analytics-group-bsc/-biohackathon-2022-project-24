import requests
from requests.exceptions import HTTPError

import xml.etree.ElementTree as ET
import sqlite3
import gzip
import io
import logging
import os
import yaml


logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

mongo_cred_path = os.path.join(
    os.path.dirname(__file__),
    "../config",
    config_all["mongodb_params"]["cred_filename"],
)
mongodb_credentials = yaml.safe_load(open(mongo_cred_path))[
    "mongodb_credentials"]


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


def commitToDatabase(c, pmcid, dictSection, dictMetadata, supMaterial):
    c.execute(f'''INSERT OR IGNORE INTO Main
    values ("{pmcid}", "{dictSection["Intro"]}", "{dictSection["Method"]}",
    "{dictSection["Result"]}", "{dictSection["Discussion"]}", "{supMaterial}",
     "{dictMetadata["issn"]["ppub"]}", "{dictMetadata["issn"]["epub"]}",
     "{dictMetadata["journalTitle"]}", "{dictMetadata["publisherName"]}")''')
    # c.commit()


def createDatabase(c):
    c.execute('''DROP TABLE IF EXISTS Main''')
    c.execute('''CREATE TABLE IF NOT EXISTS "Main" (
        "pmcid"	TEXT NOT NULL,
        "Introduction"	TEXT,
        "Methods" TEXT,
        "Result" TEXT,
        "Discussion" TEXT,
        "SupMaterial" TEXT,
        "ISSN PPUB" TEXT,
        "ISSN EPUB" TEXT,
        "JournalTitle" TEXT,
        "PublisherName" TEXT,
        PRIMARY KEY("pmcid")
            )''')


def apiSearch(pmcid, root_url):
    req = f'{root_url}{pmcid}/fullTextXML'
    r = requests.get(req)
    if not r:
        return
    root = ET.fromstring(r.content)
    if not root.findall('body'):
        return
    return root


def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    api_root_archive = config_all['api_europepmc_params']['archive_api']['root_url']
    db_file = config_all['sql_params']['db_file']

    # Name of the database

    # # Connect to the SQLite database
    # # If name not found, it will create a new database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    dummyCounter = 0
    createDatabase(c)
    OAUrl = requests.get(api_root_archive)
    gzFile = OAUrl.content
    f = io.BytesIO(gzFile)
    with gzip.GzipFile(fileobj=f) as OAFiles:
        for OAFile in OAFiles:
            dummyCounter += 1
            pmcid = str(OAFile[:-1], "utf-8")
            article = apiSearch(pmcid, api_root_article)
            if article:
                section = retrieveSections(article)
                meta_data = retrieveMetadata(article)
                sup_material = retrieveSupplementary(article)
                commitToDatabase(c, pmcid, section, meta_data, sup_material)
        print(dummyCounter)


if __name__ == "__main__":
    main()
