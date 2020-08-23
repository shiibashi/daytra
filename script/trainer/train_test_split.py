import os
from . import extract
import numpy
from .param import *

def run(df, output_dirpath):
    os.makedirs(output_dirpath, exist_ok=True)
    os.makedirs("{}/train".format(output_dirpath), exist_ok=True)
    os.makedirs("{}/test".format(output_dirpath), exist_ok=True)

    

    n = len(data_list)
    for i, d in enumerate(data_list):
        ymd = d["ymd"]
        ba = d["ba"]
        df = d["data"]
        
        picked_df = extract.pick_every_n(df, 30)
        picked_df = append_label(picked_df)
        x_arr, y_arr = to_npy(picked_df)
        
        train_test_dir = "train" if i < n * (1 - TEST_RATE) else "test"
        numpy.save("{}/{}/x_{}_{}".format(output_dirpath, train_test_dir, ymd, ba), x_arr)
        numpy.save("{}/{}/y_{}_{}".format(output_dirpath, train_test_dir, ymd, ba), y_arr)
        
def to_npy(df):
    x_list = []
    y_list = []
    for i in df.head(140).sample(30).index:
        if i < BACK_STEP:
            continue
        x = df[i-BACK_STEP:i][FEATURE_COLUMNS].values
        x_list.append(x)
        y = df.loc[i][TARGET_COLUMNS].values
        y_list.append(y)
    return numpy.array(x_list), numpy.array(y_list).astype(numpy.int)

def append_label(df):
    df = df.copy()
    df["profit"] = calc_profit_list(df)
    df["profit_flag_positive"] = df["profit"].apply(lambda x: 1 if x > 0.005 else 0)
    df["profit_flag_negative"] = df["profit"].apply(lambda x: 1 if x <= 0.005 else 0)
    return df

def calc_profit_list(df):
    profit_list = []
    for i, row in df.iterrows():
        start_value = row["upper_price"]
        if len(df[i:]) <= 1:
            profit_list.append(0)
            continue
        future_df = df[i+1:]
        profit = _calc_profit(start_value, future_df)
        profit_list.append(profit)
    return profit_list
    
def _calc_profit(start_value, future_df):
    for p in future_df["upper_price"]:
        rate = p / start_value - 1
        if rate >= WIN_LINE:
            profit = WIN_LINE
            return profit
        elif rate <= LOSE_LINE:
            profit = LOSE_LINE
            return profit
    return rate
