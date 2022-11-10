import requests
from requests.exceptions import HTTPError
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed


from section_tagger import section_tag, retrieveSections


import logging
import os
import json
import yaml
from tqdm import tqdm
import pathlib
import urllib.parse

from bs4 import BeautifulSoup

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
        return response


def apiSearch(pmcid, root_url):
    req = f'{root_url}{pmcid}/fullTextXML'
    r = requests.get(req)
    if not r:
        return
    soup = BeautifulSoup(r.content, 'lxml')
    return soup


def get_species(pmcid, annotation_url, accepted_species):
    url = annotation_url
    pmcid = f'PMC:{pmcid[3:]}'
    payload = {'articleIds': pmcid,
               'type': 'Organisms',
               'section': 'Methods',
               'provider': 'Europe PMC',
               # 'provider': requests.utils.quote('Europe PMC'),
               'format': 'JSON'}

    params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    result = get_request(url, params)
    try:
        result_json = result.json()
        species = None
        for dictionary in result_json:
            for d in dictionary['annotations']:
                species = d['exact']
                break
        if species in accepted_species:
            return pmcid
    except AttributeError:  # When not getting anything
        pass


def getPMCidList(file_location):
    with open(file_location, 'r') as f:
        for l in f:
            yield l.rstrip()


def tag_xml(soup):
    return section_tag(soup)


def recording_pmcid(pmcid, annotation_api, accepted_species, api_root_article, article_folder):
    if get_species(pmcid, annotation_api, accepted_species):
        # if True:
        article = apiSearch(pmcid, api_root_article)

        filename_xml = article_folder + pmcid + '.xml'
        try:
            with open(filename_xml, 'w') as f:
                f.write(article.prettify())
            parsed_xml = tag_xml(article)
            if parsed_xml:
                filename_json = article_folder + pmcid + '.jsonl'
                json_file = retrieveSections(parsed_xml)
                with open(filename_json, 'w') as o:
                    json.dump(json_file, o)
        except AttributeError:
            pass


    return pmcid


def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    annotation_api = config_all['api_europepmc_params']['annotations_api']['root_url']

    ids_query_location = config_all['search_params']['ids_query_location']
    article_query_folder = config_all['api_europepmc_params']['article_query_folder']

    dl_archive = config_all['search_params']['dl_archive']
    rerun_archive = config_all['search_params']['rerun_archive']
    ids_archive_location = config_all['search_params']['ids_archive_location']
    article_archive_folder = config_all['api_europepmc_params']['article_archive_folder']
    list_parsed_ids_location = config_all['api_europepmc_params']['list_parsed_ids_location']

    accepted_species = config_all['search_params']['accepted_species']

    if dl_archive is True:
        file_location = ids_archive_location
        article_folder = article_archive_folder
    else:
        file_location = ids_query_location
        article_folder = article_query_folder

    pmcid_to_dl = set(getPMCidList(file_location))
    print(f"Len of pmcid_to_dl: {len(pmcid_to_dl)}")
    # already_dl_pmcid = list()

    list_parsed_ids = list()
    try:
        with open(list_parsed_ids_location, 'r') as f:
            for l in f:
                list_parsed_ids.append(l.rstrip())
    except FileNotFoundError:
        pass
    # already_dl_pmcid = [x.stem for x in pathlib.Path(
    #     article_folder).glob("*.xml")]

    # list_pmcid = [
    #     pmcid for pmcid in pmcid_to_dl if pmcid not in list_parsed_ids]

    list_parsed_ids = set(list_parsed_ids)
    ids_to_dl = list(pmcid_to_dl.difference(list_parsed_ids))

    # n = 0
    # for pmcid in list(pmcid_to_dl):
    #     if pmcid in list_parsed_ids:
    #         pmcid_to_dl.remove(pmcid)
    #     n+=1
    #     print(f'Done {n} ids, size pcm_to_dl: {len(pmcid_to_dl)}')


    print(f"Len list_pmcid: {len(ids_to_dl)}")
    # for pmcid in tqdm(list_pmcid):
    #     recording_pmcid(pmcid, annotation_api, accepted_species,
    #                     api_root_article, article_folder)
    with tqdm(total=len(ids_to_dl)) as progress:
        futures = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=10) as ppe:
            total_recorded = 0
            for pmcid in ids_to_dl:
                future = ppe.submit(recording_pmcid, pmcid, annotation_api,
                                    accepted_species, api_root_article, article_folder)

                future.add_done_callback(lambda p: progress.update())
                futures.append(future)
                # # get the result from the task
                exception = future.exception()
                # handle exceptional case
                if exception:
                    raise(exception)

                else:
                    result = future.result()
                    if result:
                        with open(list_parsed_ids_location, 'a') as f:
                            f.write(result)
                            f.write('\n')
                        # list_parsed_ids.append(result)
                        # total_recorded += 1
                        # print(
                        #     f'Total recorded articles: {total_recorded}')

    # print(f"Recorded {total_recorded} articles from the total of {len(list_pmcid)}")


if __name__ == "__main__":
    main()
