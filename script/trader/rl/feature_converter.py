STATE_COLUMNS = ["over_under", "hms"]

def convert(df, i):
    hms = df["hms"][i]
    ymd = df["ymd"][i]
    upper_price = df["upper_price"][i]
    over_under = df["over_under"][i]
    delta_volume = df["delta_volume"]

    hms_feature = hms_to_value(hms)
    return [over_under, hms_feature]


def hms_to_value(hms):
    return 0.1
