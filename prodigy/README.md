### Structure
This folder contains the following files:
* `prodigy_config.yaml` contains the model and database path. Change to adapt to the path where the model and database are.
* `ner_output_to_prodigy_input.py` fetches entries from the database, anntates them with the model, and returns a jsonl file to input into prodigy
* `prodigy.json` contains custom variables to change how prodigy is displayed.


### Requirements
The environment must have the following packages:
* prodigy
* transformers
* torch
* nltk
* word2number


### Example of use:
`python ner_output_to_prodigy_input.py --output annotations.jsonl`
`python -m prodigy mark bh_23 annotations.jsonl  --label sample,n_male,n_female,perc_male,perc_female --view-id ner_manual`

After using prodigy, get the annotations from the json file:

`prodigy db-out bh_23 > final_annotations.jsonl`


