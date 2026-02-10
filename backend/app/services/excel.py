import pandas as pd

def read_excel(file):
    df = pd.read_excel(file.file)
    return df.to_dict(orient="records")
