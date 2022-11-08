# pipeline

## Download EuropePMC samples from list of pmcids

```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

To download the sample data:
```
python use_api.py 
```

Currently the sample comes from the query "eLIfe AND ((HAS_FT:Y AND OPEN_ACCESS:Y))"

If you want to explore different sets of data go to: https://europepmc.org/
* Do your query
* Download the ids in "Export citations" and save the result in data/
* Indicate the new file in the config "ids_file_location"