import argparse
import os
import sys
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification,logging
import torch
import logging as os_logging
import re
import json
from nltk.tokenize import sent_tokenize
import sqlite3
import tqdm
import yaml


'''
This function takes the output of the ner model and formats it into
the spans that prodigy expects
'''
def format_ner_spans(classfied_tokens, classfied_tokens_2):

    spans = []
    
    for t in classfied_tokens:
        span = {}
        span['text']= t['word']
        span['label']= t['entity']
        span['start']= t['start']
        span['end']= t['end']

        spans.append(span)

    # Getting the index (token level)
    final_spans = []
    for sp in spans:
        index_start = -1
        index_end = -1
        for t in classfied_tokens_2:
            if(sp['start'] == t['start']  ):
                index_start = t['index']
            
            if(sp['end'] == t['end']  ):
                index_end = t['index']
                sp['token_start'] = index_start
                sp['token_end'] = index_end

                final_spans.append(sp)
                break

    return final_spans


'''
This function returns a dictionary pertaining to one token and
its position in the text 
'''
def _get_token_dict(token_decoded, start, end, id, index, join_tokens):

    token_dict = {}
    # Not sure if this is the right solution if this messes up the indicies when the annotations are corrected in prodigy
    # Check this and see if there is a setting for the tokenizer to make the ## not appear
    # If I do this here, I have to also do it in the tokens so that the character indicies are correct,
    # Basically remove the ## before prodigy, annotate in prodigy, and then add ## back before using for training the model
    if token_decoded.startswith("##"):
        token_dict['text'] = token_decoded[2:] 
    else:
        token_dict['text'] = token_decoded
    
    if join_tokens == True:
        token_dict['ws'] = False
    else:
        token_dict['ws'] = True

    token_dict['id'] = id               # id is the token number
    token_dict['index'] = index         # index is ??
    
    
    
    if token_decoded == "[CLS]":
        token_dict['start'] = 0
        token_dict['end'] = 0
        token_dict['disabled'] = True
    elif token_decoded == "[SEP]":
        token_dict['start'] = 0
        token_dict['end'] = 0
        token_dict['disabled'] = True
    else:
        # Start and end are at the char level
        token_dict['start'] = start
        token_dict['end'] = end
        token_dict['disabled'] = False
    
    return token_dict


'''
This function returns a list of dicts (one dict per token)
so that prodigy does not have to tokenize the text
    
Example of a dict = {"text":"How","start":0,"end":3,"id":0}
'''
def tokens_to_prodigy_dict(tokenizer, txt_to_tokenize):

    # Tokenize and return tokens and not tensors
    encoded_sequence = tokenizer(txt_to_tokenize)["input_ids"]

    list_of_tokens = []
    char_counter = 0
    join_tokens = False
    for i,token in enumerate(encoded_sequence):
        
        if i < len(encoded_sequence)-1:
            next_token = tokenizer.decode(encoded_sequence[i+1])
            if next_token.startswith("##"):
                join_tokens = True

        token_decoded = tokenizer.decode(token)
        # If the current token should be concatenated with the previous token, subtract 
        # one from the char counter to account for no space being between the tokens
        if token_decoded.startswith("##"):
            char_counter -= 1
        token_dict = _get_token_dict(token_decoded, 
                                     start = char_counter ,
                                     end = char_counter +  len(token_decoded), 
                                     id=token,
                                     index=i,
                                     join_tokens=join_tokens
                                     )
        if token_decoded != "[CLS]" and token_decoded != "[SEP]":
            char_counter += (len(token_decoded) + 1)

        list_of_tokens.append(token_dict)
        join_tokens = False

    return list_of_tokens


'''
This function runs the model
This is somewhat specific to the tokenizer and model and that was create in BH2022, because 
we have to run the model sentence by sentence of the methods sections and then join the results
of each sentence into one results per methods section
'''
def run_classifier(methods, classifier, tokenizer):

    joined_annotations = []
    # Split methods into array of sentences
    sentences = sent_tokenize(methods)
    truncated_sentences = [s[:512] for s in sentences]

    # Run model on array 
    annotations = classifier(truncated_sentences)
    char_buffer = 0
    token_buffer = 0
    # Loop through annotations and associated sentences
    for sentence, annotation in zip(truncated_sentences, annotations):
        for dict in annotation:
            # Add buffer to start and end indexes
            dict['start'] += char_buffer 
            dict['end'] += char_buffer
            dict['index'] += token_buffer
            # Add modified dictionary to list of final dictionaries
            joined_annotations.append(dict)
        # Set new char and token buffer, adding current sentence
        char_buffer += (len(sentence))
        token_buffer += len(tokenizer(sentence)["input_ids"]) - 2       # -2 for the start and end buffers 

    return joined_annotations


'''
This function runs the model on the given methods sections and formats the results 
in prodigy annotation format
''' 
def get_annotations(methods , pmcid, classifier, classifier_2, tokenizer):

    doc_json = {}
    doc_json['text'] = methods

    cf = run_classifier(methods, classifier, tokenizer)
    cf2 = run_classifier(methods, classifier_2, tokenizer)

    doc_json['spans'] = format_ner_spans(cf, cf2)

    # Adding all tokens info
    list_of_tokens_prodigy_format = tokens_to_prodigy_dict(tokenizer = tokenizer, 
                                                           txt_to_tokenize = doc_json['text'] 
                                                           )                                                 
    doc_json['tokens'] = list_of_tokens_prodigy_format

    # Additional metadata
    meta = {}
    meta['pmcid'] = pmcid
    doc_json['meta'] = meta

    return doc_json

'''
This function queries the database to get methods sections
'''
def get_methods(db_file, limit_value):

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    SQL_QUERY = 'SELECT sections.pmcid, sections.METHODS FROM sections LIMIT ?;'
    cur.execute(SQL_QUERY,(limit_value,))
    return cur.fetchall()


def parse_args():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("--data_folder",
                        default='/gpfs/projects/bsc02/sla-projects/BioHackathon2022/biohackathon-2022-project-24/data/',
                        help="Folder where methods sections data is located"    # OR WHEN EDITED, WHERE THE RAW MODEL OUTPUT DATA IS LOCATED
                        )
    parser.add_argument("--device",
                        default=-1,
                        help="Device torch id (whether to use the GPU or not, 0 for GPU, -1 for CPU)"
                        )
    parser.add_argument("--output",
                        default='annotations.jsonl',
                        help="Where to save the annotation info (e.g. output.jsonl)"
                        )
    args = parser.parse_args()

    return args


def main(*args, **kwargs):

    # Load command line aruments 
    args = parse_args(*args, **kwargs)
    assert args.output is not None, 'You must specify an output path!'
    data_folder = args.data_folder
    device = args.device

    # Load config
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(os.path.dirname(__file__), "prodigy_config.yaml")
    config_all = yaml.safe_load(open(config_path))
    
    # Instantiate nlp pipeline
    MODEL = config_all['model_info']['model_path']
    print(f'USING MODEL:{MODEL}')
    # NOTE: I dont think I need both classifiers, just the none, because I think
    # is for when an annotations can fall under multiple classes, check with Adri
    classifier = pipeline("ner", model=MODEL, aggregation_strategy=None)    # simple strategy is for ...
    classifier_2 = pipeline("ner", model=MODEL, aggregation_strategy=None)      # no strategy is for ... 
    #tokenizer = AutoTokenizer.from_pretrained(MODEL, device = args.device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, device = args.device, do_basic_tokenize=True) 
    print("Established classifier and tokenizer")

    # Connect to database and get methods sections 
    DB_FILE = config_all["database"]["db_file"]
    print("Fetching methods sections from database...")
    # Second argument is the limit of entries you want to gather with the query, remove this here and from the function if you want to get all
    entries = get_methods(DB_FILE, 10)
    print("Methods fetched:", len(entries))

    # Loop through the data in the data folder, run the model on the entries, and turn the model output into prodigy annotations format
    with open(args.output,'w') as fout:
        print("Getting annotations for methods...")
        for row in entries:
            pmcid, methods = row
            if methods is not None:
                methods_annotated = get_annotations( methods , pmcid, classifier, classifier_2, tokenizer)
                json.dump(methods_annotated, fout)
                fout.write('\n')
                fout.flush()


if __name__ == '__main__':
    main()


'''
Innvocation example:
    python3 ner_output_to_prodigy_input.py --output annotations.jsonl
    python3 -m prodigy mark bh_23 annotations_script.jsonl  --label sample,n_male,n_female,perc_male,perc_female --view-id ner_manual


Prodigy format example:
    {"text" : "... methods section text ...",
    "spans" : [..., {"text": "125", "label": "sample", "start": 373, "end": 376, "token_start": 70, "token_end": 70}, ...], 
    "tokens" : [..., {"text": "study", "id": 2817, "index": 7, "start": 36, "end": 41, "disabled": false}, ...]}
'''