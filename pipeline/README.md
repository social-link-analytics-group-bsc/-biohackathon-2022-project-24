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
python section_tagger.py -f data/articles/ -o data/clean_articles/
```

Currently the sample comes from the query "eLIfe AND ((HAS_FT:Y AND OPEN_ACCESS:Y)) AND (((SRC:MED OR SRC:PMC OR SRC:AGR OR SRC:CBA) NOT (PUB_TYPE:"Review")))"

If you want to explore different sets of data go to: https://europepmc.org/
* Do your query
* Download the ids in "Export citations" and save the result in data/
* Indicate the new file in the config "ids_file_location"

## Explore the sections

### Tables

Explore all the tables in the jsons by running:
```
python explore_tables.py
```

To find the occurrences of a particular word (e.g. "female"):
```
python explore_tables.py | grep "female" | wc -l
```

### Methods

Find the sentences containing the tokens ['man', 'woman', 'male', 'female', 'men', 'women', 'males', 'females'] with a number before it:
```
python explore_methods.py
```

## get articles info

1. metadata given a csv containing list of pmcids and directory containing xml of the articles

```
python more_filtering.py -f data/ids-10.csv -d data/articles/        
```

2. add annotations info about `Organisms` annotated in the articles 

```
python add_annotation_info.py -f data/ids-10.csv  -a Organisms
```