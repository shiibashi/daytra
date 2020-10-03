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
import converter.convert
import trader.rl_trader

RLTRADER = trader.rl_trader.RLTrader()
RLTRADER.set_agent()

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


class LogExtractedData(BaseModel):
    upper_price: List[float]
    over_under: List[float]
    hms: List[str]
    ymd: List[str]
    delta_volume: List[float]

class LogFeatureData(BaseModel):
    hms: List[str]
    upper_price: List[float]
    over_under: List[float]
    ymd: List[str]
    upper_price_slope_5: List[float]
    upper_price_slope_25: List[float]
    upper_price_slope_75: List[float]
    upper_price_ma_5: List[float]
    upper_price_ma_25: List[float]
    upper_price_ma_75: List[float]
    running_time: List[int]
    open_over_under: List[float]
    position: List[int]

@app.get("/")
def index(request: Request):
    return {'connect': 'OK'}

@app.post("/post/test")
def post_test(data: TestData):
    return {"request_data": {"string": data.string, "lists": data.lists}}

@app.post("/post/prod/log_extract")
def post_log_extract(data: LogProcessedData):
    """
        入力: ログデータ
        出力: １分単位のログデータ
    """
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
        "pandas_data": {
            "upper_price": list(new_df["upper_price"]),
            "over_under": list(new_df["over_under"]),
            "hms": list(new_df["hms"]),
            "delta_volume": list(new_df["delta_volume"]),
            "ymd": list(new_df["ymd"])
        },
        "pandas_columns": load.OUTPUT_COLUMNS
    }
    return response


@app.post("/post/prod/log_to_feature")
def post_log_to_feature(data: LogExtractedData):
    """
        入力: １分単位のログデータ
        出力: 特徴量データ
    """
    df = pandas.DataFrame({
        "ymd": data.ymd,
        "upper_price": data.upper_price,
        "over_under": data.over_under,
        "hms": data.hms,
        "delta_volume": data.delta_volume
    })

    new_df = converter.convert.run(df)
    pandas_data = {}
    for col in converter.convert.OUTPUT_COLUMNS:
        pandas_data[col] = list(new_df[col])
    response = {
        "pandas_data": pandas_data,
        "pandas_columns": converter.convert.OUTPUT_COLUMNS
    }
    return response

@app.post("/post/prod/rl_predict")
def post_rl_predict(data: LogFeatureData):
    """
        入力: 特徴量データ
        出力: 強化学習推論結果
    """
    df = pandas.DataFrame({
        "hms": data.hms,
        "upper_price": data.upper_price,
        "over_under": data.over_under,
        "ymd": data.ymd,
        "upper_price_slope_5": data.upper_price_slope_5,
        "upper_price_slope_25": data.upper_price_slope_25,
        "upper_price_slope_75": data.upper_price_slope_75,
        "upper_price_ma_5": data.upper_price_ma_5,
        "upper_price_ma_25": data.upper_price_ma_25,
        "upper_price_ma_75": data.upper_price_ma_75,
        "running_time": data.running_time,
        "open_over_under": data.open_over_under
    })
    action, q = RLTRADER.predict(df, 0, data.position)
    response = {
        "action": action,
        "q_value": q,
        "buy_tau": RLTRADER.buy_tau,
        "sell_tau": RLTRADER.sell_tau
    }
    return response
