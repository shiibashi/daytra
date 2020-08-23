import pandas
import datetime

def pick_every_n(df, n):
    # n秒ごとにdataを抽出
    data_list = []
    while True:
        if len(df) == 0:
            break
        data_list.append(df.head(1))
        hms = df["hms"].values[0]
        dt = datetime.datetime.strptime(hms, "%H-%M-%S")
        next_dt = dt + datetime.timedelta(seconds=n)
        next_hms = next_dt.strftime("%H-%M-%S")
        df = df[df["hms"] >= next_hms].reset_index(drop=True)
    picked_df = pandas.concat(data_list, axis=0).reset_index(drop=True)
    return picked_df
