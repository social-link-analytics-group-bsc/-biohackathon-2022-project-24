import os, sys, csv, random
import yaml
from nltk.tokenize import sent_tokenize, word_tokenize
# nltk.download('punkt') # uncomment the first time you run the script
from pathlib import Path
from tqdm import tqdm
import utils.relevant_tags
import utils.extract_info as uei

config_path = os.path.join(os.path.dirname(
    __file__), '../config', 'config.yaml')
config_all = yaml.safe_load(open(config_path))

dl_folder_location = config_all['api_europepmc_params']['article_human_folder']
entire_files_to_parse = list(Path(dl_folder_location).glob("*.xml"))
entire_files_to_parse_random = random.sample(entire_files_to_parse, 100)

relevant_tags = [x for x in utils.relevant_tags.tag_locations.keys()]

metadata_tags = ['AUTHOR']

result = []


for ix, file_ in tqdm(enumerate(entire_files_to_parse_random)):
    pmcid = file_.stem
    all_tags = uei.get_content(file_, metadata_tags, article_type='research-article')
    result.append(all_tags)
    if ix == 100:
        print(pmcid)

print(result)

