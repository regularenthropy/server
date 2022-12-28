import pickle
import re
import MeCab
import demoji
import pandas as pd
import numpy as np

import msg

def Wakati(text, mecab):
    s = text.replace("|", "")
    s = re.sub(r"《.+?》", "", s)
    s = re.sub(r"［.+?］", "", s)
    s = re.sub(r"#(.*)\s{1,2}", "", s)
    s = demoji.replace(string=s, repl="")
    return mecab.parse(text)

def Predict(text, model, vector):
    df = pd.DataFrame(np.array([text]), columns=["text"])
    target_vec = vector.transform(df["text"])
    return model.predict(target_vec)[0]

def chk_text(Text):
    MeCabArg = '-Owakati -D /app/mecab/mecab-ipadic-neologd'
    ModelPath = "/app/models/MODEL_2022-12-10-01-28-30.pkl"

    # Model Load
    modelfile = pickle.load(open(ModelPath, "rb"))
    vector = modelfile[0]
    model = modelfile[1]

    # Wakati
    mecab = MeCab.Tagger(MeCabArg)
    mecab.parse("")
    wakati = Wakati(Text, mecab=mecab)

    # Predict
    result = Predict(wakati, model=model, vector=vector)

    msg.dbg(f"Text: {Text}  Result: {result}")
    return result
