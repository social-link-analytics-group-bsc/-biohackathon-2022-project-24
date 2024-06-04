import argparse
import os
import sys
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification, logging
import torch
import logging as os_logging
import re
import json
from nltk.tokenize import sent_tokenize
import sqlite3
import spacy
from tqdm.auto import tqdm
import yaml
from word2number import w2n
import re

def is_number(text):
    '''Return true if the string is a number'''
    # List of words incorrectly labelled as numbers
    not_numbers = ['point']

    try:
        w2n.word_to_num(text)
        isnumber = True if text not in not_numbers else False
    except:
        isnumber = False
    return isnumber

def get_prodigy_tokens(text, tokenizer):
    '''Get tokens in prodigy format'''
    # Tokenize the text & get offsets
    encoded_input = tokenizer(text, return_offsets_mapping=True)
    offset_mappings = encoded_input['offset_mapping']
    tokens = tokenizer.convert_ids_to_tokens(encoded_input['input_ids']) # Tokens include ['CLS'] & ['SEP']
    
    prodigy_tokens = []
    for id, (token, (start, end)) in enumerate(zip(tokens, offset_mappings)):
        
        # Add token to prodigy_tokens
        token = token[2:] if token.startswith('##') else token
        token_dict = {
            'text': token,
            'id': id,
            'start': start,
            'end': end,
            'ws': id+1 == len(tokens) or end != offset_mappings[id+1][0] # Whitespace
        }
        if not is_number(token):
            token_dict['style'] = {'color': 'grey'} # Color in grey all non-numeric words
        prodigy_tokens.append(token_dict)

    return prodigy_tokens


def get_prodigy_spans(sents_annotations: list, doc, pmcid: str, tokenizer):
    '''
    Fix offsets in sents_annotations and return prodigy-format spans
    '''
    text = doc.text
    sentences = doc.sents

    def add_current_span(current_span, char_offset, token_offset, text, pmcid):
        '''
        Fix offsets, ensure span is correct, and add to prodigy_spans
        '''
        # Fix sentence and token offsets
        current_span['start'] += char_offset
        current_span['end']   += char_offset
        current_span['token_start'] += token_offset
        current_span['token_end']   += token_offset
        
        # Ensure offsets match with the text. Else, raise error
        text_span = text[current_span['start']:current_span['end']].lower()
        assert current_span['text'].strip('#') == text_span, f"Span doesn't coincide with text: {current_span['text']} != {text_span}.PMCID: {pmcid}\n{text[current_span['start']-100:current_span['end']+100]}" 

        # Append to prodigy_spans
        prodigy_spans.append(current_span)
        return


    prodigy_spans =  []
    char_offset = 0
    token_offset = 0
    
    for sentence, entities in zip(sentences, sents_annotations):
        char_offset = sentence.start_char
        if len(entities) != 0:
            current_span = None
            for entity in entities:
                
                if current_span and entity['start'] == current_span['end'] and entity['entity'] == current_span['label']:
                    # Extend the current span: merge numbers together
                    current_span['text'] += entity['word'].strip('##')  # TODO - This won't account for things like "thirty six"
                    current_span['end'] = entity['end']
                    current_span['token_end'] = entity['index']        

                else:
                    # Finish the previous span if it exists
                    if current_span:
                        add_current_span(current_span, char_offset, token_offset, text, pmcid)
        
                    # Start a new span
                    current_span = {
                        'text' : entity['word'],
                        'label': entity['entity'],
                        'start': entity['start'],
                        'end'  : entity['end'],
                        'token_start': entity['index'],
                        'token_end'  : entity['index']
                    }

            # Add the last span if the loop ends
            if current_span:
                add_current_span(current_span, char_offset, token_offset, text, pmcid)

        # Update token offset
        token_offset += len(tokenizer.tokenize(sentence.text))
    
    return prodigy_spans


def get_annotations(doc, pmcid, classifier, tokenizer) -> dict:
    '''
    Run the model on 1 method secton and return the dict doc_json for 1 method section,
    which has the prodigy annotation format.
    doc_json structure is defined at the end of the document (Prodigy format example) 
    '''
    
    # Run model & get annotations by sentence
    sentences = doc.sents
    truncated_sents = [sent.text[:512] for sent in sentences]
    sents_annotations = classifier(truncated_sents)

    # Get tokens and spans
    prodigy_tokens = get_prodigy_tokens(doc.text, tokenizer)
    prodigy_spans  = get_prodigy_spans(sents_annotations, doc, pmcid, tokenizer)   

    # Create document dict
    doc_json = {
        'text':   doc.text,
        'spans':  prodigy_spans,
        'tokens': prodigy_tokens
    }
    
    # Add metadata
    meta = {
        'pmcid': pmcid,
    }
    doc_json['meta'] = meta

    return doc_json


def postprocess_methods_from_db(SQLentries):
    '''Remove empty methods sections, and add spaces between title and text'''

    # Instantiate a lists
    pmcids = []
    methods = []

    # REGEX
    # Define the list of words to add space after, if not followed by a space or 's' and a space
    title_words = ['method(s|ology|ologies)', 'samples', 'subjects', 'patients', 'participants', 'materials', 'setting[s]?', 'procedure[s]?', 'dataset[s]?', 'statement[s]?', 'population[s]?', 'collection[s]?', 'preparation[s]?', 'ethic[s]?', 'system[s]?', 'culture[s]?']

    # Join the words into a regex pattern, using '|'. Add a look-ahead to check for a space or [),.]
    pattern = r'(' + '|'.join(title_words) + ')(?![\s\),.])'

    # Define a replacement function that adds a space at the end of the matched word
    def add_space(match):
        return match.group(0) + ' '

    # Save only those where methods is not None
    for pmcid, methods_sect in SQLentries:
        if methods_sect is not None:
            pmcids.append(pmcid)
            # Use re.sub() to replace the matched patterns with the same text plus a space
            corrected_methods_sect = re.sub(pattern, add_space, methods_sect, flags=re.IGNORECASE)
            methods.append(corrected_methods_sect)

    return pmcids, methods

def get_methods_from_db(db_file, limit_value, offset_value=0) -> list:
    '''Query SQL db to get the methods section of [a subset of] the PMIDs in the db'''

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    SQL_QUERY = 'SELECT sections.pmcid, sections.METHODS FROM sections LIMIT ? OFFSET ?;'
    cur.execute(SQL_QUERY,(limit_value, offset_value))
    SQLentries = cur.fetchall()

    pmcids, methods = postprocess_methods_from_db(SQLentries)

    print(f"Methods fetched: {len(SQLentries)}, from which {len(methods)} are not None", )

    return pmcids, methods


def parse_args():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("--data_folder",
                        default='/gpfs/projects/bsc02/sla-projects/BioHackathon2022/biohackathon-2022-project-24/data/',
                        help="Folder where methods sections data is located"    # OR WHEN EDITED, WHERE THE RAW MODEL OUTPUT DATA IS LOCATED
                        )
    parser.add_argument("--output",
                        default='annotations.jsonl',
                        help="Where to save the annotation info (e.g. output.jsonl)"
                        )
    args = parser.parse_args()

    return args


def main(*args, **kwargs):

    # Load command line arguments 
    args = parse_args(*args, **kwargs)
    assert args.output is not None, 'You must specify an output path!'
    data_folder = args.data_folder  # TODO - Remove? Unused variable

    # Load config
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(os.path.dirname(__file__), "prodigy_config.yaml")
    config_all = yaml.safe_load(open(config_path))
    
    # Instantiate nlp pipeline
    MODEL = config_all['model_info']['model_path']
    print(f'USING MODEL:{MODEL}')
    classifier = pipeline("ner", model=MODEL, aggregation_strategy=None)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    print("Classifier and tokenizer loaded")

    # Use spacy nlp to separate the text into sentences
    # Install with:
    #pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz
    nlp = spacy.load("en_core_sci_md")
    print("Spacy sentenciser loaded")

    # Connect to database and get methods sections 
    DB_FILE = config_all["database"]["db_file"]
    print("Fetching methods sections from database...")
    # Second argument is the limit of entries you want to gather with the query, remove this here and from the function if you want to get all
    pmcids, methods = get_methods_from_db(DB_FILE, 2000, 2000) 

    batch_size = 50  # Adjust batch size based on your memory constraints
    # Open the output file outside the loop
    with open(args.output, 'w') as fout:
        print("Getting annotations for methods...")

        # Process the documents in batches. Disable components of nlp.pipe to speed up the process
        for doc, pmcid in tqdm(zip(nlp.pipe(methods, disable=['tagger', 'ner', 'lemmatizer', 'textcat'], batch_size=batch_size), pmcids), total=len(pmcids)):
            
            # Get annotations ready for prodigy
            methods_annotated = get_annotations(doc, pmcid, classifier, tokenizer)
            
            # Write the annotations for the current document to the file
            json.dump(methods_annotated, fout)
            fout.write('\n')  # Write a newline character after each JSON object
            fout.flush()

    print(f'Annotations saved in {args.output}')

if __name__ == '__main__':
    main()


'''
Innvocation example:
    python3 ner_output_to_prodigy_input.py --output annotations.jsonl
    
    python3 -m prodigy mark bh_23 annotations_script.jsonl  --label sample,n_male,n_female,perc_male,perc_female --view-id ner_manual


Prodigy format example:
    {"text" : "... methods section text ...",
    "spans" : [..., {'text': '125', 'start': 376, 'end': 379, 'token_start': 70, 'token_end': 70, 'label': 'sample'}, ...], 
    "tokens" : [..., {'text': 'methods', 'id': 1, 'start': 0, 'end': 7, 'disabled': False}, ...]}
'''