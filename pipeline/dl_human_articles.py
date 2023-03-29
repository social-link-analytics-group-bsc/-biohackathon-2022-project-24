import requests
from requests.exceptions import HTTPError
import concurrent.futures
import random
import logging
import os
import yaml
from tqdm import tqdm
import urllib.parse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def get_request(url, payload=None):
    if payload:
        params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    else:
        params = None
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


def api_search(pmcid, root_url):
    req = f'{root_url}{pmcid}/fullTextXML'
    r = requests.get(req)
    if not r:
        return
    soup = BeautifulSoup(r.content, 'lxml')
    return soup


def get_pmcidlist(file_location):
    with open(file_location, 'r') as f:
        for l in f:
            pmcid, *species = l.split(',')
            yield pmcid.rstrip().lower(), [spec.rstrip().lower() for spec in species]


def recording_pmcid(api, pmcid, dl_folder):
    recorded = True
    article = api_search(pmcid, api)

    filename_xml = dl_folder + pmcid + '.xml'
    try:
        with open(filename_xml, 'w') as f:
            f.write(article.prettify())
    except AttributeError:
        recorded = False
    return pmcid, recorded


def get_parsed_list(file_location):
    try:
        with open(file_location, 'r') as f:
            for l in f:
                yield l.split(',')[0].rstrip()
    except FileNotFoundError:
        pass


def get_list_to_dl(pmcid_todl_location, pmcid_alreadydl_location, human_terms):
    """
    Parse the list of pmcid which contains the species.
    Subselect only the ones that contains one of the
    term associated to human, and remove the one already dl
    """
    def check_species(specie_list, human_terms):
        if any(x in human_terms for x in specie_list):
            return True
    pmcid_to_dl = [pmcid for pmcid, species in get_pmcidlist(
        pmcid_todl_location) if check_species(species, human_terms)]


    pmcid_to_dl=set(pmcid_to_dl)
    print(f"Len of pmcid_to_dl: {len(pmcid_to_dl)}")

    list_parsed=set(
        get_parsed_list(pmcid_alreadydl_location))
    print(f"Len of already done: {len(list_parsed)}")

    ids_to_dl=list(pmcid_to_dl.difference(list_parsed))
    print(f"Len of pmcid to parse: {len(ids_to_dl)}")
    # Randomize the list to avoid downloading only the first articles
    random.shuffle(ids_to_dl)
    return ids_to_dl


def main():
    rest_api=config_all['api_europepmc_params']['rest_articles']['root_url']

    article_folder_location=config_all['api_europepmc_params']['article_human_folder']
    pmcid_species_file=config_all['api_europepmc_params']['pmcid_species_file']
    human_terms=config_all['search_params']['human_terms']
    pmcid_human_downloaded_file=config_all['api_europepmc_params']['pmcid_human_downloaded_file']

    ids_to_dl=get_list_to_dl(
        pmcid_species_file, pmcid_human_downloaded_file, human_terms)
    futures=[]
    executor=concurrent.futures.ThreadPoolExecutor()
    print('Starting the process')
    futures=[executor.submit(recording_pmcid, rest_api, pmcid, article_folder_location)
               for pmcid in ids_to_dl]

    print('Process started. Getting results')
    pbar=tqdm(total=len(ids_to_dl))  # Init pbar
    with open(pmcid_human_downloaded_file, 'a') as f:
        for future in concurrent.futures.as_completed(futures):

            result_pmcid, result_record=future.result()
            f.write(f"{result_pmcid}, {str(result_record)}")
            f.write('\n')
            pbar.update(n=1)
            exception=future.exception()
            if exception:
                raise (exception)
            if result_record is False:
                print(f'Did not recorded: {result_pmcid}')


if __name__ == "__main__":
    main()
