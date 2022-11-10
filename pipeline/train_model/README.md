## Transform the annotations to conll format

```
python annoations_to_conll.py
```

## Train the model to extract the number of male and female

```
sh train_model.sh
```

## Use the model to infere where is the info

```
cd ..
python get_sex_bias.py --data data/candidate_sentences_last.csv --out results.json --model train_model/model
```