import logging
import os
from pathlib import Path
import csv
from tqdm import tqdm
import yaml
import xml.etree.ElementTree as ET
from collections import defaultdict

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

logger = logging.getLogger(__name__)


def parse_xml(tree, level_counts, tag_counts, attr_val_counts):
    level_parsed = set()
    tag_parsed = set()
    attr_val_parsed = set()

    try:
        root = tree.getroot()
        for child in root.findall('.//article/*'):
            if child.tag not in level_parsed:
                level_counts[child.tag] += 1
                level_parsed.add(child.tag)
            for c in child.iter():
                tag_key = f"{child.tag}{c.tag}"
                if tag_key not in tag_parsed:
                    tag_counts[child.tag][c.tag] += 1
                    tag_parsed.add(tag_key)
                for attr in c.attrib:
                    try:
                        attr_val = c.attrib[attr]
                    except ValueError:
                        attr_val = 'NA'
                    attr_val_key = f"{child.tag}{c.tag}{attr}{attr_val}"
                    if attr_val_key not in attr_val_parsed:
                        attr_val_counts[child.tag][c.tag][attr][attr_val] += 1
                        attr_val_parsed.add(attr_val_key)
    except AttributeError:
        pass
    return level_counts, tag_counts, attr_val_counts


def open_file(file_location):
    return open(file_location, 'r')


def get_tree_xml(xml_file):
    try:
        return ET.parse(xml_file)
    except ET.ParseError:  # In case of empty file
        return


def record_results(file_location, results, header, mode, record_type):
    with open(file_location, mode) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        if mode == 'w':
            writer.writeheader()
        if record_type == 'level':
            for level in results:
                writer.writerow({'level': level, 'count': results[level]})
        elif record_type == 'tag':
            for level in results:
                content_tag = results[level]
                for tag in content_tag:
                    count = content_tag[tag]
                    writer.writerow({'level': level, 'tag': tag, 'count': count})

        elif record_type == 'attr':
            for level in results:
                content_tag = results[level]
                for tag in content_tag:
                    content_attr = content_tag[tag]
                    for attr in content_attr:
                        content_attr_val = content_attr[attr]
                        for attr_val in content_attr_val:
                            count = content_attr_val[attr_val]
                            writer.writerow({'level': level, 'tag': tag, 'attr': attr, 'attr_val': attr_val, 'count': count})
    csv_file.close()


def main():
    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
    sentence_location = config_all['processing_params']['sentence_location']
    interesting_tokens = config_all['processing_params']['token_sentences']
    list_level_location = config_all['processing_params']['list_level_location']
    list_tags_location = config_all['processing_params']['list_tag_location']
    list_attr_val_location = config_all['processing_params']['list_attr_val_location']

    entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))

    header_level = ['level', 'count']
    header_tag = ['level', 'tag', 'count']
    header_attr_val = ['level', 'tag', 'attr', 'attr_val', 'count']
    count = 0
    mode = 'w'

    level_counts = defaultdict(int)
    tag_counts = defaultdict(lambda: defaultdict(int))
    attr_val_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
    for file_ in tqdm(entire_files_to_parse):
        xml = open_file(file_)
        tree = get_tree_xml(xml)
        current_levels, current_tags, current_attr_val = parse_xml(tree, level_counts, tag_counts, attr_val_counts)
        count += 1
        if count % 1000 == 0:

            record_results(list_level_location, current_levels, header_level, mode, 'level')
            record_results(list_tags_location, current_tags, header_tag, mode, 'tag')
            record_results(list_attr_val_location, current_attr_val, header_attr_val, mode, 'attr')
    record_results(list_level_location, current_levels, header_level, mode, 'level')
    record_results(list_tags_location, current_tags, header_tag, mode, 'tag')
    record_results(list_attr_val_location, current_attr_val, header_attr_val, mode, 'attr')


if __name__ == "__main__":
    main()
