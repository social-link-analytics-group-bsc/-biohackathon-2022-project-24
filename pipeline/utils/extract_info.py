import xml.etree.ElementTree as ET

import logging
logger = logging.getLogger(__name__)
from utils.relevant_tags import tag_locations


def get_root(file_location):
    """
    Open the file location and parse it to xml.
    Args:
        file_location (str): The location of the xml file.
    Returns:
        tree (xml.etree.ElementTree): The parsed xml tree.
    """
    try:
        f = open(file_location, 'r')
        tree = ET.parse(f)
        return tree
    except ET.ParseError:
        return


def get_article_type(tree, article_type):
    """
    Check if the article type is matching the desired type.
    Args:
        tree (xml.etree.ElementTree): The parsed xml tree.
        article_type (str): The desired article type.
    Returns:
        xml.etree.Element: The article element if the article type matches the desired type,
        None otherwise.
    """
    article = tree.find('.//article')
    if article.attrib['article-type'] == article_type:
        return article


def extract_content(root, level, tag=None, attr=None, attr_val=None):
    """
    Extract the content from the xml.
    Args:
        root (xml.etree.ElementTree): The parsed xml tree.
        level (str): The level to extract the content from.
        tag (str): The tag to extract the content from.
        attr (str): The attribute of the tag to extract the content from.
        attr_val (str or list of str): The attribute value of the tag to extract the content from.
    Returns:
        str: the content extracted from the xml.
    """

    def iterate(node, path, tag):
        if path:
            current_path = path + "/" + node.tag
        else:
            current_path = node.tag
        for child in node:
            if child.tag == tag:
                return child
            iterate(child, path=current_path, tag=tag)

    result = set()
    query = f".//{level}//{tag}[@{attr}]"
    for element in root.findall(query):
        for el in element.iter():
            if el.attrib.get(attr, '').strip().lower() in attr_val:
                print(ET.tostringlist(el))
                text = el.text
                # text = text.strip()
                print(text)
                result.add(text)

    try:
        # return '\n'.join(result)
        return result
    except TypeError:
        return


def return_unique_dict(values):

    # Workout to avoid doing several time the same parsing
    # Should be put outside loop but require to rewrite everything

    already_done = set()
    for value in values:
        val_to_access = tag_locations[value]
        level = val_to_access['level']
        tag = val_to_access['tag']
        attr = val_to_access['attr']
        attr_val = val_to_access['attr_val']
        final_val = list()

        # In case there is only value for attr_val, need to convert in list
        if isinstance(attr_val, str):
            attr_val = [attr_val]

        for val in attr_val:
            to_check = f'{level}_{tag}_{attr}_{val}'
            if to_check not in already_done:
                final_val.append(val)
                already_done.add(to_check)

        # for attr_value in final_val:
        yield level, tag, attr, final_val


def extract_value(xml, values):
    """
    Extract the desired values from the xml.
    Args:
        xml (xml.etree.ElementTree): The parsed xml tree.
        values (str or list of str): The values to extract from the xml.
    Returns:
        str: the content extracted from the xml.
    """
    # As they can have duplicate results when passing different values
    # Use set to remove them
    # Todo: rather than set, should avoid to parse several time the same
    # Section and check the values from the relevant_tags dictionary before

    results = list()
    if isinstance(values, str):
        values = [values]
    for level, tag, attr, attr_val in return_unique_dict(values):
        result = extract_content(xml, level, tag, attr, attr_val)
        if result:
            results.append(result)
    try:
        # results = '\n'.join(results)
        return results
    except TypeError:
        return


def get_content(file_location, values, article_type='research-article'):
    """
    Get the content from the xml file.
    Args:
        file_location (str): The location of the xml file.
        values (str or list of str): The values to extract from the xml.
        article_type (str): The desired article type.
    Returns:
        str: the content extracted from the xml.
    """
    xml = get_root(file_location)
    if xml:
        root = get_article_type(xml, article_type)
        if root:
            return extract_value(root, values)


def multiple_content(file_location, dictionary_values, article_type='research-article'):
    """
    Get multiple content from the xml file.
    Args:
        file_location (str): The location of the xml file.
        dictionary_values (dict): The different values needed to be return with each key a separated one and
        the value where to find it
        article_type (str): The desired article type.
    Returns:
        dict: the content extracted from the xml per key
    """
    dict_result = dict()
    for content in dictionary_values:
        result = get_content(file_location, dictionary_values[content], article_type)
        dict_result[content] = result
    return dict_result
