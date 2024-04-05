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
`annotations.jsonl`, created with `ner_output_to_prodigy_input.py`, is used to pre-annotate the method sections that can then be revised with prodigy.
```
python ner_output_to_prodigy_input.py --output annotations.jsonl
prodigy mark bh_23 annotations.jsonl  --label sample,n_male,n_female,perc_male,perc_female,sample_p,n_male_p,n_female_p,perc_male_p,perc_female_p --view-id ner_manual
```

When annotation has finished, save the annotations in a jsonl file:
```
prodigy db-out bh_23 > final_annotations.jsonl
```


