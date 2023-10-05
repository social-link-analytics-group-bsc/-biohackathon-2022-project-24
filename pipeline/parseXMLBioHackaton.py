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
import json
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

def create_tables(conn, table_sections, table_mesh_tags, table_metadata):

    c = conn.cursor()

    c.execute(
        f"""CREATE TABLE IF NOT EXISTS "{table_sections}" (
	            "pmcid"	TEXT NOT NULL,
                "api_response" TEXT NOT NULL,
	            "introduction" TEXT,
	            "methods" TEXT,
	            "result" TEXT,
	            "discussion" TEXT,
	            PRIMARY KEY("pmcid")
            )"""
    )
    conn.commit()
    c.execute('''CREATE TABLE IF NOT EXISTS "{table_metadata}" (
                "pmcid"	TEXT,
	            "title"	TEXT,
                "abstract"	TEXT,
	            "issn_ppub" TEXT,
                "issn_epub" TEXT,
                "publisherName" TEXT,
                "year"	INTEGER,
                "doi"	TEXT,
	            "ISSN" TEXT,
                "ISOAbbreviation" TEXT,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )''')
    conn.commit()

    c.execute(f'''CREATE TABLE IF NOT EXISTS "{table_mesh_tags}" (
	            "pmid"	INTEGER NOT NULL,
	            "descriptionName" TEXT,
                "descriptionUI" TEXT,
                "qualifierName" TEXT,
                "qualifierUI" TEXT,
	            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )''')
    conn.commit()
    c.execute(
            f"""CREATE TABLE IF NOT EXISTS "{table_check}" (
            "pmcid" TEXT NOT NULL,
            "api_response" TEXT NOT NULL,
            "parsing" INTEGER,
            "results" INTEGER,
            FOREIGN KEY("pmcid") REFERENCES "{table_sections}"("pmcid")
            )"""
   conn.commit() 

def retrieve_pmcids(conn):

    c = conn.cursor()
    # Execute a SELECT query to retrieve the pmcid values
    c.execute("SELECT pmcid FROM {table_check}")

    # Fetch all the pmcid values and store them in a list
    pmcid_list = [row[0] for row in c.fetchall()]
    c.close()
    return pmcid_list


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

def retrieveMetadata(root, metadata_fields):
    dictMetadata = {
            "issn_ppub": None,
            "issn_epub": None,
            "publisher_name": None,
            "title" : None,
            "year" : None,
            "publication_type":None,
            "pubmed_id" : None,
            "doi_id" : None,
            "pmc_id" : None,
            "journal_title":None,
            "ISSN" : None,
            'abstract': None, 
            "ISO_abbrevation" : None}

    for front in root.iter("front"):
        for journalId in front.iter("issn"):
            if "ppub" in journalId.attrib["pub-type"]:
                dictMetadata["issn_ppub"] = "".join(journalId.itertext())
            if "epub" in journalId.attrib["pub-type"]:
                dictMetadata["issn_epub"] = "".join(journalId.itertext())
        for journalTitle in front.iter("journal-title"):
            dictMetadata["journal_title"] = "".join(journalTitle.itertext())
        for publisher in front.iter("publisher-name"):
            dictMetadata["publisher_name"] = "".join(publisher.itertext())

    for article in root.iter("PubmedArticle"):
        for title_atr in article.iter("ArticleTitle"):
            title = ''.join(title_atr.itertext())   # Take all text and the tags inside them
            dictMetadata["title"] = title.replace('"', "'")         # Standarize the quotation marks
        
        for abs_atr in article.iter("AbstractText"):
            abstract = ''.join(abs_atr.itertext())   # Take all text and the tags inside them
            dictMetadata["abstract"] = abstract.replace('"', "'")         # Standarize the quotation marks
        
        # Search and store the year of publication
        for date_atr in article.iter("PubDate"):
            for year_atr in date_atr.iter("Year"):  
                dictMetadata["year"] = year_atr.text
        
        # Publication type
        pubtype_array = list()
        for pub_type in article.iter("PublicationTypeList"):
            for pub_type_atr in pub_type.iter("PublicationType"):  
                pubtype_array.append(str(pub_type_atr.text).strip())
                            
            dictMetadata["publication_type"] = pubtype_array[0]

        # Search and store the ID of the article
        # We only want the first <ArticleIdList>, because is the one having the Id of the article
        # The other <ArticleIdList> are for the references
        for articleId_atr in article.iter("ArticleIdList"):
            for Id_atr in articleId_atr.iter("ArticleId"):
                if "pubmed" in Id_atr.attrib["IdType"]:
                    dictMetadata["pubmed_id"] = Id_atr.text
                if "doi" in Id_atr.attrib["IdType"]:
                    dictMetadata["doi_id"] = Id_atr.text
                if "pmc" in Id_atr.attrib["IdType"]:
                    dictMetadata["pmc_id"] = Id_atr.text
            break
        
        # Journal Info
        for journal_info in article.iter("Journal"):
            # for sub_journal_info in journal_info.iter():
            #     print(sub_journal_info.tag, sub_journal_info.text)
            
            # Normally the journal_title is retrieved earlier in this function
            # for journal_name in journal_info.iter("Title"):
            #     dictMetadata["journal_title"] = journal_name.text
            for ISSN_attr in journal_info.iter("ISSN"):
                dictMetadata["ISSN"] = ISSN_attr.text
            for ISO_attr in journal_info.iter("ISOAbbreviation"):
                dictMetadata["ISO_abbrevation"] = ISO_attr.text
        
        # Authors List:
        # for authors in article.iter("AuthorList"):
            
    return dictMetadata



def retrieveMeshTags(article):
    list_mesh = []
    
    for mesh_tags in article.iter("MeshHeading"):
        # dictMesh = {"descriptor_label" : None,
        #             "descriptor_UI" : None,
        #             "qualifier_label" : None,
        #             "qualifier_UI" : None}

        for descriptor_attr in mesh_tags.iter("DescriptorName"):
            list_mesh.append(descriptor_attr.text)

            # dictMesh["descriptor_label"] = descriptor_attr.text
        #     dictMesh["descriptor_UI"] = descriptor_attr.attrib['UI']
        # for qualifier_attr in mesh_tags.iter("QualifierName"):
        #     dictMesh["qualifier_label"] = qualifier_attr.text
        #     dictMesh["qualifier_UI"] = qualifier_attr.attrib['UI']
        # list_mesh.append(dictMesh)

    return list_mesh

def api_search(pmcid):
    req = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    r = requests.get(req)
    if not r:
        return pmcid,  False, None
    return pmcid, True, r.content 

def parsing_xml(content)
    root = ET.fromstring(r.content)
    if root.findall("body"):
        dict_section = retrieveSections(root)
        dict_metadata = retrieveMetadata(root)
        list_mesh = retrieveMeshTags(root)
        parsing = True

    else:
        dict_section = dict()
        dict_metadata = dict()
        list_mesh = list()
        parsing = False
    return pmcid, api_response, parsing, dict_section, dict_metadata, list_mesh


def commitToDatabase(conn, pmcid, api_response, parsing, dict_section, dict_metadata, list_mesh):
    # FIXME: dirty way to check if values are present, should be done better and
    # Remove the hardcoded values to put in config file
    def format_dict_values(dict_section, dict_metadata):
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
        metadata_values = ["journal_title", "publisherName"]
        for val in metadata_values:
            values_to_record.append(dictMetadata.get(val, None))

        return values_to_record

    values_to_record = format_dict_values(dict_section, dict_metadata, list_mesh)
    c = conn.cursor()
    sql_query = f"""
    INSERT OR IGNORE INTO Main (pmcid, api_response,  issn_ppub, issn_epub, journal_title, publisherName) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
    c.execute(sql_query, values_to_record)
    conn.commit()
    c.close()

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
    
    #FIXME: Move these variables in config file or in a class data
    table_section = 'sections'
    table_metadata = 'metadata'
    table_check = 'check'

    section_fields = ["introduction", "methods", "result", "discussion"]
    metadata_fields = [
            "issn_ppub",
            "issn_epub",
            "publisher_name",
            "title",
            "year",
            "publication_type",
            "pubmed_id",
            "doi_id",
            "pmc_id",
            "journal_title",
            "ISSN",
            "abstract",
            "ISO_abbrevation"
            ]
    check_fields = ["api_response", 'parsing', 'results']

    try:
        futures = []
        executor = concurrent.futures.ThreadPoolExecutor()
        logging.info("Getting the information from the list of pmcid")
        futures = [executor.submit(api_search, pmcid) for pmcid in ids_to_dl]

        logger.info("Process started. Getting results")
        pbar = tqdm(total=len(ids_to_dl))  # Init pbar
        for future in concurrent.futures.as_completed(futures):
            pmcid, api_response, content = future.result()
            parsing, dict_sections, dict_metadata, list_mesh = parsing_xml(content)
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
