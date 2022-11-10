
XML_DATA_PATH = $1
SENTENCES = "data/candidate_sentences.csv"
MODEL = "train_model/model"
RESULTS = "results.json"

python explore_methods.py --data_path $XML_DATA_PATH --out $SENTENCES

python get_sex_bias.py --data $SENTENCES --out $RESULTS --model $MODEL


