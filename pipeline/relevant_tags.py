import logging
import yaml
import os
logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))


# Three tags are present in all documents (almost), Front, sec and back.
# They contains different type of information about the articles
# Parsing them differently can give more complete information
# These keywords are single and lowercase,
# Extracted from the sec level if they are > 5 occurences among the entire dataset dl with human subject as filter
# Ordered by descending count
# They are found using the notebook ./tag_exploration.ipynb

# The information for front is in the embedded in the tags
front_section = {'AUTHOR': ['author'],
                 'PUBLISHER': ['publisher-id'],
                 'OPEN_ACCESS': ['open-access'],
                 'AFFILIATION': ['aff']}  # Lot of different type of attr_val with aff followed by number (or without)


# The back section is back



sec_section = {'INTRO': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'intro',
        'introduction',
        'background',
        'intro|methods',
        'intro|subjects',
        'general',
        'summary',
        'intro|methods|subjects',
        'objectives',
        'opening-section',
        'aim',
        'intro|results',
        'opening',
        'description',
    ]
},

    'METHODS': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'materials|methods',
        'methods',
        'subjects',
        'materials and methods',
        'materials-and-methods',
        'materials',
        'methods|subjects',
        'material|methods',
        'subjects|methods',
        'materials-methods',
        'intro|methods',
        'intro|subjects',
        'materials | methods',
        'methods|results',
        'methods|materials',
        'method',
        'patients|methods',
        'materialsandmethods',
        'material and methods',
        'materials methods',
        'intro|methods|subjects',
        'methods|discussion'
        'materials and method',
        'materials|method'
        'materialandmethods',
        'material|method',
        'supplemental|material',
        'patients and methods',
        'survey|methodology',
        'methods|conclusions'
        'materials|methods',
        'materials|methodology',
        'methods|cases',
        'methods and materials',
        'methodology',
        'intro|methods|results',
        'material|methods'
    ],
},

    'SUBJECTS': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'subjects',
        'methods|subjects',
        'subjects|methods',
        'intro|subjects',
        'patients|methods',
        'intro|methods|subjects',
        'patients and methods',
        'subjects|results',
        'subjects|discussion',
        'sampling description',
        'species'
    ],
},
    'RESULTS': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'results',
        'results|discussion',
        'result',
        'methods|results',
        'results and discussion',
        'results|conclusions',
        'results | discussion',
        'discussion|results',
        'results|discussion',
        'intro|results',
        'intro|methods|results',
        'finding',
        'diagnosis'
    ],
},

    'DISCUSSION': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'discussion',
        'discussions',
        'results|discussions',
        'discussions',
        'results|discussion',
        'disucssion|conclusions',
        'results and discussion',
        'discussion|conclusion',
        'discussion|interpretation',
        'methods|discussion',
        'results | discussion',
        'discuss',
        'discusion',
        'discussion|results',
        'subjects|discussion',
        'result|discussion',
        'discussion | conclusions',
        'conclusion|discussion'
    ],
},
    'CONCLUSION': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'conclusions',
        'conclusion',
        'discussion|conclusions',
        'summary',
        'discussion|conclusion',
        'perspectives',
        'results|conclusions',
        'limitations',
        'discussion | conclusions',
        'conclusion|discussion'
        'research highlights',
        'key messages',
    ],
},
    'ACK_FUND': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'funding-information',
        'acknowledgement',
        'acknowledgment',
        'funding',
        'acknowledgements',
        'financial-disclosure',
        'funding sources',
        'funding-statement'
        'aknowledgement',
        'acknowlegement',
        'open access',
        'financial support',
        'grant',
        'author note',
        'financial disclosure'],
},
    'AUTH_CONT': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        "author-contributions",
        "authors' contributions",
        "author contributions",
        "authors' contribution",
        "author-contributor",
        "contribution"],
},
    'COMP_INT': {
    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'disclaimer',
        'conflict of interest',
        'competing interests',
        'conflict of interests',
        'disclaimar',
        'disclosure|statement'
    ],
},
    'SUPPL': {

    'tag': 'sec',
    'attr': 'sec-type',
    'attr_val': [
        'supplementary-material',
        'supplemental|material'],
}
}

back_section = {}
