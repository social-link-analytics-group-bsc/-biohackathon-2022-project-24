import os
import sys
import re
import json
import random
from tqdm import tqdm
from pathlib import Path
import xml.etree.ElementTree as ET

import concurrent.futures
import logging
import yaml
logger = logging.getLogger(__name__)

# sys.path.append("/gpfs/projects/bsc08/bsc08494/BH22/repo_def/biohackathon-2022-project-24/pipeline/utils")

from utils.relevant_tags import tag_locations
from utils.extract_info import get_content


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def main():

    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']

    entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))
    entire_files_to_parse = random.sample(entire_files_to_parse, 1000)

    interesting_fields = ['METHODS']

    # dict_value = sec_section

    for file_ in tqdm(entire_files_to_parse):
        pmcid = file_.stem
        method_text = get_content(file_, interesting_fields, article_type='research-article')
        print(pmcid, method_text)


if __name__ == "__main__":
    main()
