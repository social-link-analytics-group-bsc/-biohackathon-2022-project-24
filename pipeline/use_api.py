import requests
from requests.exceptions import HTTPError

import xml.etree.ElementTree as ET
import logging
import os
import yaml
from tqdm import tqdm
import pathlib
import urllib.parse
from urllib.parse import quote


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
    root = ET.fromstring(r.content)
    if not root.findall('body'):
        return
    return root


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
    result_json = result.json()
    species = None
    for dictionary in result_json:
        for d in dictionary['annotations']:
            species = d['exact']
            break
    if species in accepted_species:
        return pmcid



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
    annotation_api = config_all['api_europepmc_params']['annotations_api']['root_url']
    file_location = config_all['search_params']['ids_file_location']
    article_folder = config_all['api_europepmc_params']['article_folder']
    accepted_species = config_all['search_params']['accepted_species']
    pmcid_to_dl = list(getPMCidList(file_location))
    print(f"Len of pmcid_to_dl: {len(pmcid_to_dl)}")
    already_dl_pmcid = list()

    already_dl_pmcid = [x.stem for x in pathlib.Path(article_folder).glob("*.xml")]

    list_pmcid = [pmcid for pmcid in pmcid_to_dl if pmcid not in already_dl_pmcid]

    print(f"Len list_pmcid: {len(list_pmcid)}")
    for pmcid in tqdm(list_pmcid):
        print(pmcid)
        if get_species(pmcid, annotation_api, accepted_species):
            article = apiSearch(pmcid, api_root_article)
            tree = ET.ElementTree(article)
            with open('data/articles/'+pmcid+'.xml', 'wb') as f:
                tree.write(f)

if __name__ == "__main__":
    main()
