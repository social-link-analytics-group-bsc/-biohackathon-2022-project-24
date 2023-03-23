# Three tags are present in all documents (almost), Front, sec and back.
# They contains different type of information about the articles
# Parsing them differently can give more complete information
# These keywords are single and lowercase,
# Extracted from the sec level if they are > 5 occurences among the entire dataset dl with human subject as filter
# Ordered by descending count
# They are found using the notebook ./tag_exploration.ipynb

# The information for front is in the embedded in the tags

tag_locations = {
    'PUBLISHER': {
        'level': 'front',
        'tag': 'journal-id',
        'attr': 'journal-id-type',
        'attr_val': 'publisher-id'
    },
    'YEAR': {
        'level': 'front',
        'tag': 'date',
        'attr': 'date-type',
        'attr_val': 'accepted'
    },
    'AUTHOR': {
        'level': 'front',
        'tag': 'contrib',
        'attr': 'contrib-type',
        'attr_val': 'author'
    },
    'INTRO': {
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
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
        'level': 'sec',
        'tag': 'sec',
        'attr': 'sec-type',
        'attr_val': [
            'conflict of interest',
            'competing interests',
            'conflict of interests',
            'disclaimar',
            'disclosure|statement'
        ],
    },
    'SUPPL': {

        'level': 'sec',
        'tag': 'sec',
        'attr': 'sec-type',
        'attr_val': [
            'supplementary-material',
            'supplemental|material'],
    }
}
