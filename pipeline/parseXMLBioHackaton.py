# Import libraries
import concurrent.futures
import requests
import xml.etree.ElementTree as ET
import sqlite3
import sys
import os
import yaml
import logging
import random
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(__file__), "../config", "config.yaml")
config_all = yaml.safe_load(open(config_path))


# Never worked in supplementary material, don't know what to expect
# Ok we comment it out as we don't need it
# I remove any ref of it in the createDatabase(), commitToDatabase(), apiSearch() [Olivier]
# def retrieveSupplementary(root):
#     for supplementary in root.iter("supplementary-material"):
#         return str(ET.tostring(supplementary)).replace('"', "'")


def retrieveMetadata(root):
    dictMetadata = {
        "issn": {"ppub": "", "epub": ""},
        "journalTitle": "",
        "publisherName": "",
    }

    for front in root.iter("front"):
        for journalId in front.iter("issn"):
            if "ppub" in journalId.attrib["pub-type"]:
                dictMetadata["issn"]["ppub"] = "".join(journalId.itertext())
            if "epub" in journalId.attrib["pub-type"]:
                dictMetadata["issn"]["epub"] = "".join(journalId.itertext())
        for journalTitle in front.iter("journal-title"):
            dictMetadata["journalTitle"] = "".join(journalTitle.itertext())
        for publisher in front.iter("publisher-name"):
            dictMetadata["publisherName"] = "".join(publisher.itertext())
    return dictMetadata


# Retrieve the text for each section
def retrieveSections(root):
    dictSection = {"Intro": "", "Method": "", "Result": "", "Discussion": ""}
    for body in root.iter("body"):
        for child in body.iter("sec"):
            if "sec-type" in child.attrib:
                for section in dictSection.keys():  # For each section in dictSection
                    # Sections inside sec-type are written in the following form:
                    # intro, methods, results, discussion
                    if section.lower() in child.attrib["sec-type"].lower():
                        dictSection[section] = "".join(child.itertext()).replace(
                            '"', "'"
                        )  # Text without tags
                        # dictSection[section] = ET.tostring(child) # Text with tags
            if child[0].text:
                for section, sectionData in dictSection.items():
                    if sectionData:
                        continue
                    if section.lower() in child[0].text.lower():
                        dictSection[section] = "".join(child.itertext()).replace(
                            '"', "'"
                        )  # Text without tags
                        # dictSection[section] = ET.tostring(child) # Text with tags
    return dictSection


def createDatabase(conn):

    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS "Main" (
	            "pmcid"	TEXT NOT NULL,
                "api_response" TEXT NOT NULL,
	            "Introduction" TEXT,
	            "Methods" TEXT,
	            "Result" TEXT,
	            "Discussion" TEXT,
	            "issn_ppub" TEXT,
                "issn_epub" TEXT,
                "journalTitle" TEXT,
                "publisherName" TEXT,
	            PRIMARY KEY("pmcid")
            )"""
    )
    conn.commit()


def retrieve_pmcids(conn):

    c = conn.cursor()
    # Execute a SELECT query to retrieve the pmcid values
    c.execute("SELECT pmcid FROM Main")

    # Fetch all the pmcid values and store them in a list
    pmcid_list = [row[0] for row in c.fetchall()]
    c.close()
    return pmcid_list


def apiSearch(pmcid):
    req = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    r = requests.get(req)
    if not r:
        api_response = False
        return pmcid, api_response, dict(), dict()
    else:
        api_response = True
    root = ET.fromstring(r.content)
    if root.findall("body"):
        dictSection = retrieveSections(root)
        dictMetadata = retrieveMetadata(root)
    else:
        dictSection = dict()
        dictMetadata = dict()
    return pmcid, api_response, dictSection, dictMetadata


# FIXME: dirty way to check if values are present, should be done better and
# Remove the hardcoded values to put in config file


def format_values(pmcid, api_response, dictSection, dictMetadata):
    values_to_record = []
    values_to_record.append(pmcid)
    values_to_record.append(api_response)
    sections_values = ["Intro", "Method", "Result", "Discussion"]
    for val in sections_values:
        values_to_record.append(dictSection.get(val, None))
    issn_values = ["ppub", "epub"]
    try:
        for val in issn_values:
            values_to_record.append(dictMetadata["issn"].get(val, None))
    # In case the issn key is not present, add as much none as the values needed
    except KeyError:
        for _ in range(len(issn_values)):
            values_to_record.append(None)
    metadata_values = ["journlaTitle", "publisherName"]
    for val in metadata_values:
        values_to_record.append(dictMetadata.get(val, None))
    return values_to_record


def commitToDatabase(conn, values_to_record):

    c = conn.cursor()
    sql_query = f"""
    INSERT OR IGNORE INTO Main (pmcid, api_response, Introduction, Methods, Result, Discussion, issn_ppub, issn_epub, journalTitle, publisherName) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
    c.execute(sql_query, values_to_record)
    conn.commit()
    c.close()


def get_list_to_dl(pmcid_location, list_parsed):
    def get_list_humans(file_location):
        try:
            with open(file_location, "r") as f:
                for l in f:
                    yield l.split(",")[0].rstrip()
        except FileNotFoundError:
            raise

    list_humans = set(get_list_humans(pmcid_location))
    logger.info(f"Len of complete list of human pmcid: {len(list_humans)}")
    logger.info(f"Len of already done species: {len(list_parsed)}")

    ids_to_dl = list(list_humans.difference(set(list_parsed)))
    logger.info(f"Len of pmcid to parse: {len(ids_to_dl)}")
    # Randomize the list to avoid downloading only the first articles
    random.shuffle(ids_to_dl)
    return ids_to_dl


def main():
    pmcid_human_file = config_all["api_europepmc_params"]["pmcid_human_file"]
    # # Name of the database
    DB_FILE = config_all["api_europepmc_params"]["db_info_articles"]

    # # Connect to the SQLite database
    # # If name not found, it will create a new database
    conn = sqlite3.connect(DB_FILE)
    createDatabase(conn)
    # Parse the db and get the already dl pmcids list and remove them from
    # The original list
    pmcid_db_dl = retrieve_pmcids(conn)
    ids_to_dl = get_list_to_dl(pmcid_human_file, pmcid_db_dl)
    logger.info(f"Got the list of pmcids to dl: {len(ids_to_dl)}")

    try:
        futures = []
        executor = concurrent.futures.ThreadPoolExecutor()
        logging.info("Getting the information from the list of pmcid")
        futures = [executor.submit(apiSearch, pmcid) for pmcid in ids_to_dl]

        logger.info("Process started. Getting results")
        pbar = tqdm(total=len(ids_to_dl))  # Init pbar
        for future in concurrent.futures.as_completed(futures):
            pmcid, api_response, dictSection, dictMetadata = future.result()
            values_to_record = format_values(
                pmcid, api_response, dictSection, dictMetadata
            )
            commitToDatabase(conn, values_to_record)
            pbar.update(n=1)
            exception = future.exception()
            if exception:
                logger.error(
                    "Got an exception: {exception}.\nClose the db connection and exit."
                )
                conn.close()
                raise (exception)
        conn.close()
    except Exception as e:
        logger.error(
            f"An unexpected exception occurred: {e}. Closing the db connection and exiting."
        )
        conn.close()
        raise e  # Re-raise the exception for further handling if needed


if __name__ == "__main__":
    main()
