
import logging
import os
import yaml
from tqdm import tqdm
import pathlib


logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def main():
    api_root_article = config_all['api_europepmc_params']['rest_articles']['root_url']
    annotation_api = config_all['api_europepmc_params']['annotations_api']['root_url']

    article_archive_folder = config_all['api_europepmc_params']['article_archive_folder']
    list_parsed_ids_location = config_all['api_europepmc_params']['list_parsed_ids_location']

    article_folder = article_archive_folder
    print(article_folder)

    with open(list_parsed_ids_location, 'w') as f:
        for x in pathlib.Path(article_folder).glob("*.jsonl"):
            f.write(x.stem)
            f.write('\n')

if __name__ == "__main__":
    main()
