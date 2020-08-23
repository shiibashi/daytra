import pandas
import os

def run(df):
    #df = df.copy().assign(
    #    ymd=lambda df: df["time"].apply(lambda x: x[0:10]),
    #    ba=lambda df: df["hms"].apply(lambda x: _ba(x))
    #)
    return df
    


def _ba(hms):
    if hms < "09-00-00":
        ba = "before_yori"
    elif hms < "11-30-00":
        ba = "morning"
    elif hms < "12-30-00":
        ba = "lunch"
    else:
        ba = "afternoon"
    return ba
