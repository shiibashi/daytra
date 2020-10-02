from fastapi import FastAPI
import pandas
from starlette.requests import Request
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

app = FastAPI(title='RLBOTTER', description='RLBOTTER', version='1')

sys.path.append("..")
import load

class TestData(BaseModel):
    string: str
    lists: List[float]

class LogProcessedData(BaseModel):
    ymd: str
    time: List[str]
    over: List[int]
    under: List[int]
    upper_price: List[int]
    downer_price: List[int]
    over_under: List[float]
    hms: List[str]
    volume_sum: List[int]


@app.get("/")
def index(request: Request):
    return {'connect': 'OK'}

@app.post("/post/test")
def post_test(data: TestData):
    return {"request_data": {"string": data.string, "lists": data.lists}}

@app.post("/post/prod/log_extract")
def post_log_extract(data: LogProcessedData):
    df = pandas.DataFrame({
        "time": data.time,
        "over": data.over,
        "under": data.under,
        "upper_price": data.upper_price,
        "downer_price": data.downer_price,
        "over_under": data.over_under,
        "hms": data.hms,
        "volume_sum": data.volume_sum
    })
    ymd = data.ymd
    new_df = load.extract_data(df, ymd)
    response = {
        "upper_price": list(new_df["upper_price"]),
        "over_under": list(new_df["over_under"]),
        "hms": list(new_df["hms"]),
        "delta_volume": list(new_df["delta_volume"]),
        "ymd": list(new_df["ymd"])
    }
    return response
