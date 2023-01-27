import os, sys
import re
import json
from tqdm import tqdm
from pathlib import Path
import xml.etree.ElementTree as ET

import concurrent.futures
import logging
import yaml
logger = logging.getLogger(__name__)

sys.path.append("/gpfs/projects/bsc08/bsc08494/BH22/repo_def/biohackathon-2022-project-24/pipeline/utils")

from relevant_tags import tag_locations
# from relevant_tags import front_section, sec_section, back_section


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


def clean_tag(string):
    """
    Return a list of cleaned tags from a string
    """
    # Split the string on any character that is not a letter
    words = re.split('[^a-zA-Z]', string)
    # Lowercase all the words and filter out any empty strings
    return [word.lower() for word in words if word]


def get_content(file_location, level, section_dictionary, values):

    with open(file_location, 'r') as f:

        # try:
        tree = ET.parse(f)
        root = tree.getroot()
        root = root.find(f'.//article/{level}')

        # root = root.findall('.//article/*')
        # except ET.ParseError:  # In case of empty file

        if isinstance(values, str):
            values = [values]

        for value in values:
            val_to_access = section_dictionary[value]

            try:
                tag = val_to_access['tag']
            except KeyError:
                tag = None
            try:
                attr = val_to_access['attr']
            except KeyError:
                attr = None
            try:
                attr_val = val_to_access['attr_val']
            except KeyError:
                attr_val = None
            yield extract_content(root, tag, attr, attr_val)


def extract_content(root, tag=None, attr=None, attr_val=None):


    for child in root.findall(tag):
        print(child.attrib)
        try:
            for c in child.find(attr):
                return c.attrib
                # print(len(c))
        except TypeError:
            pass

        # print(child.tag)
        # print(child)
        # if attr is None:
        #     return child.text
        # for c in child.iter():
        #     # print(c.tag)
        #     for attr in c.attrib:
        #         if attr_val is None:
        #             return c.text


def main():

    dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
    sentence_location = config_all['processing_params']['sentence_location']
    interesting_tokens = config_all['processing_params']['token_sentences']
    list_tags_location = config_all['processing_params']['list_tag_location']
    list_attr_val_location = config_all['processing_params']['list_attr_val_location']

    entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))
    relevant_tags = [x for x in tag_locations.keys()]

    # to_parse = ['SUBJECTS', "METHODS"]

    # dict_value = sec_section
    dict_value = tag_locations
    file_count = 0

    for file_ in tqdm(entire_files_to_parse):
        parsed_info = dict()
        # for level in [('front', front_section), ('sec', sec_section), ('back', back_section)]:
        result = get_content(file_, 'sec', dict_value, relevant_tags)
        for r in result:
            print(r)
        file_count += 1
        if file_count == 100:
            break
        
        

if __name__ == "__main__":
    main()


            # print(r)
        # print(result)
#     count = 0
#     results = dict()
#     for file_ in tqdm(entire_files_to_parse):
#         # print(file_.stem)
#         try:
#             xml = open_file(file_)
#             tree = get_tree_xml(xml)
#             # try:
#             root = tree.getroot()
#             tags_names = [t.tag for t in root.findall('.//article/*')]
#             for tags in tags_names:
#                 results[tags] = results.setdefault(tags, 0) + 1
#             print(results)
#         except AttributeError:
#             pass
#             # print(child)
#             # if child:
#             #     pass
#             # else:
#             #     print(file_.stem)
#             # print(child)
#             # for tag in child.iter():
#             # print(tag)
#         # parsed_section = get_section(tree, tag_sections, 'tag')
#         count += 1
#         # if count == 1:
#         # break
#         # except AttributeError:  # Empty file_
#         #     pass
