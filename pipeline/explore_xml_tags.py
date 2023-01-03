import logging
import os
from pathlib import Path
import csv
import json
from tqdm import tqdm
import yaml
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

logger = logging.getLogger(__name__)


def parse_xml(tree):
    level_counts = dict()
    tag_counts = dict()
    attr_val_counts = dict()
    try:
        root = tree.getroot()
        for child in root.findall('.//article/*'):
            level_counts.setdefault(child.tag, 1)
            tag_counts.setdefault(child.tag, {})
            for c in child.iter():

                tag_counts[child.tag].setdefault(c.tag, 1)
                for attr in c.attrib:
                    try:
                        attr_val = c.attrib[attr]
                    except ValueError:
                        attr_val = 'NA'

                    attr_val_counts.setdefault(child.tag, {})
                    attr_val_counts[child.tag].setdefault(c.tag, {})
                    attr_val_counts[child.tag][c.tag].setdefault(attr, {})
                    attr_val_counts[child.tag][c.tag][attr].setdefault(attr_val, 1)
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


def add_dicts(d1, d2, log=False):
    # Source: https://stackoverflow.com/a/51861758
    def sum_val(v1, v2):
        if v2 is None:
            if log is True:
                print(f"No k in v2")
            return v1
        try:
            if log is True:
                print(f'adding the two val: v1 - {v1}, v2 - {v2}')
            return v1 + v2
        except TypeError:
            return add_dicts(v1, v2)
    result = d2.copy()
    if log is True:
        print(f"d1 - {d1}, d2 - {d2}")
    result.update({k: sum_val(v, d2.get(k)) for k, v in d1.items()})
    if log is True:
        print(f'Final result: {result}')
    return result


# def record_results(file_location, results):

#     with open(file_location, "w") as f:
#         json.dump(results, f)


def record_results_level(file_location, results, header, mode):
    with open(file_location, mode) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for level in results:
            writer.writerow({'level': level, 'count': results[level]})
    csv_file.close()
    return mode

def record_results_tag(file_location, results, header, mode):
    with open(file_location, mode) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for level in results:
            content_tag = results[level]
            for tag in content_tag:
                count = content_tag[tag]

                writer.writerow({'level': level, 'tag': tag, 'count': count})
        csv_file.close()
    return mode


def record_results_attr(file_location, results, header, mode):

    with open(file_location, mode) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
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
    return mode


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
    total_levels = dict()
    total_tags = dict()
    total_attr_val = dict()
    mode = 'w'
    mode_tag = 'w'
    mode_attr = 'w'

    for file_ in tqdm(entire_files_to_parse):
        # try:
        xml = open_file(file_)
        tree = get_tree_xml(xml)
        current_levels, current_tags, current_attr_val = parse_xml(tree)
        if current_levels:
            total_levels = add_dicts(total_levels, current_levels, log=False)
            total_tags = add_dicts(total_tags, current_tags)
            total_attr_val = add_dicts(total_attr_val, current_attr_val)
        count += 1
        if count == 100:
            record_results_level(list_level_location, total_levels, header_level, mode)
            record_results_tag(list_tags_location, total_tags, header_tag, mode)
            record_results_attr(list_attr_val_location, total_attr_val, header_attr_val, mode)
        #     break
        mode = 'a'
        # except AttributeError:
        #     pass

    record_results_level(list_level_location, total_levels, header_level, mode)
    record_results_tag(list_tags_location, total_tags, header_tag, mode)
    record_results_attr(list_attr_val_location, total_attr_val, header_attr_val, mode)


if __name__ == "__main__":
    main()
