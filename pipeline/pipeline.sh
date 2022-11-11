
JSON_DATA_PATH = $1
SENTENCES = $2
MODEL = $3
RESULTS = "results.json"

python explore_methods.py --data_path $JSON_DATA_PATH --out $SENTENCES

python get_sex_bias.py --data $SENTENCES --out $RESULTS --model $MODEL


