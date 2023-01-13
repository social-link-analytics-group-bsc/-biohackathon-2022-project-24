

In a VM with prodigy installed: 

```
python csv_to_jsonl.py

source prodigyenv/bin/activate

prodigy spans.manual biohack blank:ca raw.jsonl -l n_fem,n_male,perc_fem,perc_male,sample

prodigy db-out biohack > data/annotations.jsonl
```