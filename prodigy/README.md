
## Structure
This folder has the following content:

**Method sections retrieval files**
* `ner_output_to_prodigy_input.py` is the script used to retrieve, pre-annotate and pre-process the methods sections that will be afterwards inputted into Prodigy. 
* `prodigy_config.yaml` contains the model and database path. Change to adapt to the path where the model and database are.

**Annotation with Prodigy files**
* `postjuly_annotations/` contains scripts and files for the annotations done after the finalisation of the annotation guidelines:
  * `make_annotations_to_(group_|re)annotate.sh` are two scripts that create json files to be used for Prodigy
  * `make_screens.sh` is used to create a screen with subscreens to launch one Prodigy Server for each of the jsonl files created with the previous scripts
  * `prodigy.json` contains custom variables to change how prodigy is displayed. Must be placed in the same folder as `make_screens.sh`

**.gitignore files**
Files not included in the GitHub. They are found in the BHG Drive <span style="color:red">TODO: Add Drive location</span>
* `mounted_gpfs/` folder where to sshfs mount the SQL database (to get the method sections) and the trained LLM model (to get the pre-annotations)
* `sensible_config.sh` contains the path of the python environment where Prodigy is installed (PRODIGY_VENV_PATH) and the BASE_PORT (not included in the GitHub for security reasons). 
* `original_annotations/` contains the 1056 methods sections that have been used for annotated throughout April - October 2024 (`original_annotations.jsonl`), created with the script `ner_output_to_prodigy_input.py`.
* `final_annotations/` contains several checkpoints of the annotations made with Prodigy

## Requirements
The environment must have the following packages:
* prodigy
* transformers
* torch
* nltk
* word2number


## Example of use:

**Basic use:**
```
python ner_output_to_prodigy_input.py --output original_annotations.jsonl
prodigy mark bh_23 annotations.jsonl  --label sample,n_male,n_female,perc_male,perc_female,sample_p,n_male_p,n_female_p,perc_male_p,perc_female_p --view-id ner_manual
```

**Postjuly annotations use**
How to prepare several servers of Prodigy for different annotators to run simultaneously:
```
# Create sensible configuration variables bash script
vim sensible_config.sh
> PRODIGY_VENV_PATH=    # Prodigy environment path 
> BASE_PORT=            # Base port where to host the prodigy servers (e.g. 855). Last digit is specified in make_screens.sh (e.g. to use ports 8550 - 8562)

# Create annotations to reannotate & load the servers
cd postjuly_annotations
bash make_annotations_to_group_annotate.sh
bash make_annotations_to_reannotate.sh
bash make_screens.sh        # Requires prodigy.json in its same folder
```

**Extracting annotations**
When annotation has finished, save the annotations in a jsonl file:
```
prodigy db-out bh_23 > final_annotations.jsonl
```