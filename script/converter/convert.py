import pandas
import os
import datetime

OUTPUT_COLUMNS = [
    "hms", "upper_price", "over_under", "delta_volume", "ymd",
    # "open", "max", "min", "close",
    #"open_yesterday", "max_yesterday", "min_yesterday", "close_yesterday",
     "upper_price_ma_5",
    "upper_price_ma_25", "upper_price_ma_75", "upper_price_slope_5", "upper_price_slope_25",
    "upper_price_slope_75", "running_time", "open_over_under"
]


def run(df):
    #daily_data = df.groupby("ymd")["upper_price"].agg(
    #    [open_value, "max", "min", close_value]
    #).reset_index().rename(columns={"open_value": "open", "close_value": "close"})
    #for col in ["open", "max", "min", "close"]:
    #    col2 = "{}_yesterday".format(col)
    #    daily_data[col2] = daily_data[col].shift(1)

    #df = df.merge(daily_data, on=["ymd"], how="left")

    df = df[0:len(df):5].reset_index(drop=True)
    df["upper_price_ma_5"] = df["upper_price"].rolling(5).mean()
    df["upper_price_ma_25"] = df["upper_price"].rolling(25).mean()
    df["upper_price_ma_75"] = df["upper_price"].rolling(75).mean()

    df["upper_price_slope_5"] = df["upper_price_ma_5"].pct_change(1)
    df["upper_price_slope_25"] = df["upper_price_ma_25"].pct_change(1)
    df["upper_price_slope_75"] = df["upper_price_ma_75"].pct_change(1)
    df["running_time"] = df["hms"].apply(lambda x: running_time(x))
    daily_data = df.groupby("ymd")["over_under"].agg(open_value).reset_index().rename(
        columns={"over_under": "open_over_under"})
    df = df.merge(daily_data, on=["ymd"], how="left")
    df = df.dropna().reset_index(drop=True)
    ymd_df = df.drop_duplicates(subset=["ymd"]).sort_values(
    "ymd")[["ymd"]].reset_index(drop=True).assign(ymd_index=lambda df: df.index
    )
    df = df.merge(ymd_df, on="ymd", how="inner")
    return df
    
def open_value(series):
    return list(series)[0]

def close_value(series):
    return list(series)[-1]

def running_time(hms):
    dt1 = datetime.datetime.strptime(hms, "%H-%M-%S")
    dt2 = datetime.datetime.strptime("09-00-00", "%H-%M-%S")
    return (dt1 - dt2).seconds
