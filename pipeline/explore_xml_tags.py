import logging
import os
from pathlib import Path
import csv
from tqdm import tqdm
import yaml
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

logger = logging.getLogger(__name__)


def parse_xml(xml_file, entire_tags):
    try:
        tree = ET.parse(xml_file)
        # root = tree.getroot()
        # for child in root.iter('body'):
        # tags = {elem.tag for elem in xmlTree.iter()}
        for child in tree.iter():

            # Should be single value dictionary
            for attr in child.attrib:
                try:
                    attr_val = child.attrib[attr]

                except ValueError:  # In case empty dict
                    attr = attr_val = 'NA'
                entire_tags.setdefault(child.tag, {})
                entire_tags[child.tag].setdefault(attr, {})
                entire_tags[child.tag][attr].setdefault(attr_val, 0)
                entire_tags[child.tag][attr][attr_val] += 1

            # try:
           #     entire_tags[child.tag][attr][attr_val] += 1
           # except KeyError:
           #     entire_tags[child.tag][attr][attr_val] = 1

    except ET.ParseError:  # empty doc
        pass

    return entire_tags


def main():
    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
    sentence_location = config_all['processing_params']['sentence_location']
    interesting_tokens = config_all['processing_params']['token_sentences']
    list_tags_location = config_all['processing_params']['list_tags_location']

    entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))
    entire_tags = dict()

    count = 0
    for file in tqdm(entire_files_to_parse):
        with open(file, 'r') as xml_file:
            entire_tags = parse_xml(xml_file, entire_tags)
        # count += 1
        # if count == 100:
        #     break

    header = ['tag', 'attr', 'attr_val', 'count']
    with open(list_tags_location, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        to_record = {}
        for tag in entire_tags:
            content_tag = entire_tags[tag]
            for attr in content_tag:
                content_attr = content_tag[attr]
                for attr_val in content_attr:
                    count = content_attr[attr_val]
                    writer.writerow({'tag': tag, 'attr': attr, 'attr_val': attr_val, 'count': count})


if __name__ == "__main__":
    main()
