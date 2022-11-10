import pandas as pd
import spacy
from math import isnan
# if you get an error you need to downoald
# python3 -m spacy download en_core_web_sm
# 
if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    df = pd.read_csv("new_data.csv")
    for idx in df.itertuples():
        # 
        if isinstance(idx.aff,str):
            doc = nlp(idx.aff)
            for e in doc.ents:
                if e.label_=="GPE":  
                    df.loc[idx.Index, 'Countries'] = e.text
                if e.label_=="ORG":  
                    df.loc[idx.Index, 'Organisations'] = e.text
    df.to_csv("withcountries.csv")