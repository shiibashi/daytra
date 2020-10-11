import pandas
import requests
import env


URL = "http://{}:{}".format(env.HOST, env.PORT)

def log_extract(df, ymd):
    print("log_extract")
    data = {
        "ymd": ymd,
        "time": list(df["time"]),
        "over": list(df["over"]),
        "under": list(df["under"]),
        "upper_price": list(df["upper_price"]),
        "downer_price": list(df["downer_price"]),
        "over_under": list(df["over_under"]),
        "hms": list(df["hms"]),
        "volume_sum": list(df["volume_sum"])
    }
    response = requests.post("{}/post/prod/log_extract".format(URL), json=data)
    response_data = response.json()

    new_df = pandas.DataFrame(response_data["pandas_data"], columns=response_data["pandas_columns"])
    return new_df

def log_to_feature(df):
    print("log_to_feature")
    data = {
        "ymd": list(df["ymd"]),
        "upper_price": list(df["upper_price"]),
        "over_under": list(df["over_under"]),
        "hms": list(df["hms"]),
        "delta_volume": list(df["delta_volume"])
    }
    response = requests.post("{}/post/prod/log_to_feature".format(URL), json=data)
    response_data = response.json()
    new_df = pandas.DataFrame(response_data["pandas_data"], columns=response_data["pandas_columns"])
    return new_df

def rl_predict(df, position):
    print("rl_predict")
    data = {
        "hms": list(df["hms"]),
        "upper_price": list(df["upper_price"]),
        "over_under": list(df["over_under"]),
        "ymd": list(df["ymd"]),
        "upper_price_slope_5": list(df["upper_price_slope_5"]),
        "upper_price_slope_25": list(df["upper_price_slope_25"]),
        "upper_price_slope_75": list(df["upper_price_slope_75"]),
        "upper_price_ma_5": list(df["upper_price_ma_5"]),
        "upper_price_ma_25": list(df["upper_price_ma_25"]),
        "upper_price_ma_75": list(df["upper_price_ma_75"]),
        "running_time": list(df["running_time"]),
        "open_over_under": list(df["open_over_under"]),
        "position": position
    }
    response = requests.post("{}/post/prod/rl_predict".format(URL), json=data)
    response_data = response.json()
    response_data["q_value"] = float(response_data["q_value"])
    response_data["buy_tau"] = float(response_data["buy_tau"])
    response_data["sell_tau"] = float(response_data["sell_tau"])
    return response_data

if __name__ == "__main__":
    DTYPE_2 = {
        "time": object,
        "over": int,
        "under": int,
        "upper_price": int,
        "downer_price": int,
        "over_under": float,
        "hms": object,
        "volume_sum": int
    }
    # ５分足で75個データが必要だから2日前までのデータが必要
    df_0 = pandas.read_csv("dev_data/log_processed_2020-08-11.csv", dtype=DTYPE_2)
    df_1 = pandas.read_csv("dev_data/log_processed_2020-08-12.csv", dtype=DTYPE_2)
    df_2 = pandas.read_csv("dev_data/log_processed_2020-08-13.csv", dtype=DTYPE_2)
    df_0e = log_extract(df_0, "2020-08-11")
    df_1e = log_extract(df_1, "2020-08-12")
    df_2e = log_extract(df_2, "2020-08-13")

    dfe = pandas.concat([df_0e, df_1e, df_2e], axis=0).reset_index(drop=True)
    #dfe.to_csv("tmp_extracted.csv")

    df3 = log_to_feature(dfe)
    #df3.to_csv("tmp_feature.csv")

    response = rl_predict(df3, [0])
    print(response)
