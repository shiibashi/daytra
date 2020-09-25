#STATE_COLUMNS = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"]
#STATE_COLUMNS = ["f1", "f6", "f7", "f8", "f9", "f10"]
STATE_COLUMNS = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "position"]

def convert(df, i):
    hms = df["hms"][i]
    upper_price = df["upper_price"][i]
    over_under = df["over_under"][i]
    #delta_volume = df["delta_volume"][i]
    ymd = df["ymd"][i]
    open_value = df["open"][i]
    open_value_yesterday = df["open_yesterday"][i]
    max_value_yesterday = df["max_yesterday"][i]
    min_value_yesterday = df["min_yesterday"][i]
    close_value_yesterday = df["close_yesterday"][i]
    upper_price_slope_5 = df["upper_price_slope_5"][i]
    upper_price_slope_25 = df["upper_price_slope_25"][i]
    upper_price_slope_75 = df["upper_price_slope_75"][i]

    upper_price_ma_5 = df["upper_price_ma_5"][i]
    upper_price_ma_25 = df["upper_price_ma_25"][i]
    upper_price_ma_75 = df["upper_price_ma_75"][i]
    running_time = df["running_time"][i]
    open_over_under = df["open_over_under"][i]

    f1 = running_time / 21600
    f2 = upper_price_ma_5 / upper_price
    f3 = upper_price_ma_25 / upper_price
    f4 = upper_price_ma_75 / upper_price
    f5 = upper_price_slope_5 * 100
    f6 = upper_price_slope_25 * 100
    f7 = upper_price_slope_75 * 100
    f8 = over_under / open_over_under
    return [f1, f2, f3, f4, f5, f6, f7, f8]
    #return [f1, f6, f7, f8, f9, f10]

try:
    import sapi
    STATE_COLUMNS = ["f1", "f2", "f3", "f4", "f5", "f6", "f7"]
    API = sapi.SAPI()
    API.ready(code=2413)
    def convert(df, i):
        hms = df["hms"][i]
        ymd = df["ymd"][i]
        running_time = df["running_time"][i]
        f1 = running_time / 21600
        f2 = API.get_feature("ICEBERG", ymd=ymd, hms=hms)
        f3 = API.get_feature("HELL", ymd=ymd, hms=hms)
        f4 = API.get_feature("SPRING", ymd=ymd, hms=hms)
        f5 = API.get_feature("WINNER/LOSER", ymd=ymd, hms=hms)
        f6 = API.get_feature("RESISTANCE", ymd=ymd, hms=hms)
        f7 = API.get_feature("SUPPORT", ymd=ymd, hms=hms)
        return [f1, f2, f3, f4, f5, f6, f7]
except Exception as e:
    pass
