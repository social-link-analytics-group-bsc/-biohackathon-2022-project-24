# pipeline

## Download EuropePMC samples from list of pmcids

```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

To download the sample data and transform to json:
```
python use_api.py 
python europepmc_api/OTAR_new_pipeline_section_tagger.py -f pipeline/data/articles/ -o pipeline/data/clean_articles/
```

Currently the sample comes from the query "eLIfe AND ((HAS_FT:Y AND OPEN_ACCESS:Y)) AND (((SRC:MED OR SRC:PMC OR SRC:AGR OR SRC:CBA) NOT (PUB_TYPE:"Review")))"

If you want to explore different sets of data go to: https://europepmc.org/
* Do your query
* Download the ids in "Export citations" and save the result in data/
* Indicate the new file in the config "ids_file_location"