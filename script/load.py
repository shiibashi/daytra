import pandas
import numpy
import os
import datetime
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

def read_log_data(dirpath):
    return _read_log_data_with_volume(dirpath)


def _read_log_data_with_volume(dirpath):
    filepath_list = sorted(os.listdir(dirpath))
<<<<<<< HEAD
=======
    dtype = {
        "time": object,
        "over": int,
        "under": int,
        "upper_price": int,
        "downer_price": int,
        "volume_sum": int,
        "over_under": float,
        "hms": object
    }
>>>>>>> 011511c... s
    df_list = []
    for f in filepath_list:
        print(f)
        s = f.split("_")
        ymd = s[2].replace(".csv", "")
<<<<<<< HEAD
        df = pandas.read_csv("{}/{}".format(dirpath, f), dtype=DTYPE_2)
        if "volume_sum" not in df.columns:
            continue
        df = df[list(DTYPE_2.keys())].reset_index(drop=True)
        
        df_upper_price = _filter_upper_price(df)

        df_over_under = _filter_over_under(df)
        df_volume_sum = _filter_volume_sum(df)

        print(len(df_upper_price), len(df_over_under), len(df_volume_sum))
        df_upper_price["over_under"] = df_over_under["over_under"]
        df_upper_price["delta_volume"] = df_volume_sum["delta_volume"]
        df_upper_price["ymd"] = ymd       

        df_list.append(df_upper_price)
=======
        df = pandas.read_csv("{}/{}".format(dirpath, f), dtype=dtype)
        if not all([col in df.columns for col in list(dtype.keys())]):
            continue
        df = df[list(dtype.keys())]
        df_1 = _filter_1(df)
        df_2 = _filter_2(df_1)
        df_3 = _filter_3(df_2)
        df_3["ymd"] = ymd
        df_list.append(df_3)
>>>>>>> 011511c... s
    merge_df = pandas.concat(df_list, axis=0).reset_index(drop=True)
    return merge_df

def _filter_upper_price(df):
    # upper_priceの変動でフィルタリング
    before_upper_price = 0
    valid_index_list = []
    for i, row in df.iterrows():
        upper_price = row["upper_price"]
        if before_upper_price == 0:
            if 3000 <= upper_price <= 10000:
                before_upper_price = upper_price
            else:
                continue
        elif -40 <= upper_price - before_upper_price <= 40:
            valid_index_list.append(i)
            before_upper_price = upper_price
    df_valid = df.loc[valid_index_list].reset_index(drop=True)
    
    df_valid_per_1m = _filter_per_1m(df_valid)
    df_interpolated = _interpolate(df_valid_per_1m, "upper_price")
    return df_interpolated

def _filter_over_under(df):
    # upper_priceの変動でフィルタリング
    before_v = 0
    valid_index_list = []
    for i, row in df.iterrows():
        v = row["over_under"]
        if before_v == 0:
            if 0.01 <= v <= 10:
                before_v = v
            else:
                continue
        elif -1 <= v - before_v <= 1:
            valid_index_list.append(i)
            before_v = v
    df_valid = df.loc[valid_index_list].reset_index(drop=True)

    df_valid_per_1m = _filter_per_1m(df_valid)
    df_interpolated = _interpolate(df_valid_per_1m, "over_under")
    return df_interpolated

def _filter_volume_sum(df):
    # upper_priceの変動でフィルタリング
    before_v = 0
    before_hms = "09-00-00"
    hms_list = []
    volume_list = []
    for i, row in df.iterrows():
        v = row["volume_sum"]
        hms = row["hms"]
        if i == 0:
            before_v = v
            before_hms = hms
            continue
        if 0 <= v - before_v <= 50000:
            hms_list.append(hms)
            volume_list.append(v - before_v)
        before_v = v
        before_hms = hms
    df_valid = pandas.DataFrame({"hms": hms_list, "delta_volume": volume_list})


    v = df_valid["delta_volume"][0]
    start = df_valid["hms"][0]
    volume_list = [v]
    hms_list = [start]
    for i in range(len(df_valid)):
        next_hms = plus_second(start, 60)
        end_hms = plus_second(start, 600)
        tmp = df_valid[(df_valid["hms"] >= start) & (df_valid["hms"] <= end_hms)]
        if "11-30-00" <= next_hms <= "12-30-00" or len(tmp) == 0:
            start = next_hms
            continue
        s = tmp["hms"].apply(lambda x: min(second_delta(next_hms, x), second_delta(x, next_hms)))
        argmin_index = numpy.argmin(s)
        h = df_valid["hms"][argmin_index]
        v = df_valid[(df_valid["hms"] > start) & (df_valid["hms"] <= h)]["delta_volume"].mean()
        volume_list.append(v)
        hms_list.append(h)

        start = next_hms
        if argmin_index >= len(df_valid)-1:
            print("break")
            break
    df_valid_per_1m = pandas.DataFrame({"hms": hms_list, "delta_volume": volume_list})
    df_interpolated = _interpolate(df_valid_per_1m, "delta_volume")
    return df_interpolated

def _filter_per_1m(df):
    # １分ごとにフィルタリング
    valid_index_list = [0]
    start = df["hms"][0]
    for i in range(len(df)):
        next_hms = plus_second(start, 60)
        end_hms = plus_second(start, 600)
        tmp = df[(df["hms"] >= start) & (df["hms"] <= end_hms)]
        if "11-30-00" <= next_hms <= "12-30-00" or len(tmp) == 0:
            start = next_hms
            continue
        s = tmp["hms"].apply(lambda x: min(second_delta(next_hms, x), second_delta(x, next_hms)))
        argmin_index = numpy.argmin(s)
        #index = s.index[argmin_index]
        index = argmin_index
        valid_index_list.append(index)
        start = next_hms
        if index >= len(df)-1:
            print("break")
            break
    
    dfm = df.loc[valid_index_list].reset_index(drop=True)    
    return dfm


def _interpolate(df, column):
    # １分ごとに補間値で埋める
    data_list = []
    hms = df["hms"][0]
    v = df[column][0]
    data_list.append([hms, v])
    next_hms = hms
    while next_hms <= "14-59-00":
        next_hms = plus_second(hms, 60)
        if "11-30-00" < next_hms < "12-30-00":
            hms = next_hms
            v = v_2
            continue
        tmp = df[df["hms"] >= next_hms]
        if len(tmp) == 0:
            break
        v_2, hms_2 = tmp[column].values[0], tmp["hms"].values[0]
        v_x = interpolate(hms, v, hms_2, v_2, next_hms)
        data_list.append([next_hms, v_x])

        hms = next_hms
        v = v_2
    df2 = pandas.DataFrame(data_list, columns=["hms"]+[column])
    return df2


def second_delta(hms_1, hms_2):
    # hms_1 - hms_2秒
    dt1 = datetime.datetime.strptime(hms_1, "%H-%M-%S")
    dt2 = datetime.datetime.strptime(hms_2, "%H-%M-%S")
    s = (dt1 - dt2).seconds
    return s

def plus_second(hms, n):
    # hms + n秒
    dt = datetime.datetime.strptime(hms, "%H-%M-%S")
    plus_dt = dt + datetime.timedelta(seconds=n)
    plus_hms = plus_dt.strftime("%H-%M-%S")
    return plus_hms

def interpolate(hms, up, hms_2, up_2, next_hms):
    # (hms, up), (hms_2, up_2)の2点上にある(next_hms, x)の点のxを求める
    assert next_hms > hms
    if next_hms == hms_2:
        x = up_2
    elif next_hms > hms_2:
        # (hms, up), (hms_2, up_2),(next_hms, x)の位置関係
        t_1 = second_delta(next_hms, hms)
        t_2 = second_delta(hms_2, hms)
        x = up + (up_2 - up) * (t_1 / t_2)
    else:
        # (hms, up),(next_hms, x), (hms_2, up_2)の位置関係
        t_1 = second_delta(next_hms, hms)
        t_2 = second_delta(hms_2, hms)
        a = t_1 / t_2
        x = up * (1 - a) + up_2 * a
    return x
