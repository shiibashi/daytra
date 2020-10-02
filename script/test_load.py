import pandas
import numpy
import os
import datetime
import load


def test_filter_per_1m():
    df = pandas.read_csv("dev_data/log_processed_2020-08-13.csv", dtype=load.DTYPE_2)
    df2 = load._filter_per_1m(df)
    print(df2["hms"])
    hms_list = _9_15_1m()
    assert len(df2) < len(hms_list) + 2
    for hms in df2["hms"]:
        assert in60(hms, hms_list)

def test_filter_volume_sum():
    df = pandas.read_csv("dev_data/log_processed_2020-08-13.csv", dtype=load.DTYPE_2)
    df2 = load._filter_volume_sum(df)
    hms_list = _9_15_1m()
    assert len(df2) < len(hms_list) + 2
    for hms in df2["hms"]:
        assert in60(hms, hms_list)
    for v in df2["delta_volume"]:
        assert v >= 0

def in60(hms, hms_list):
    for v in hms_list:
        s = load.second_delta(hms, v)
        if -60 <= s <= 60:
            return True
    return False

def _9_15_1m():
    hms = "09-00-00"
    hms_list = [hms]
    while hms < "15-00-00":
        next_hms = load.plus_second(hms, 60)
        hms_list.append(next_hms)
        hms = next_hms
    return hms_list

if __name__ == "__main__":
    test_filter_per_1m()
    test_filter_volume_sum()
