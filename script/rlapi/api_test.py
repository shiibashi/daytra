import pandas
import requests
import env


URL = "http://{}:{}".format(env.HOST, env.PORT)

def test_connect():
    print("test_connect")
    response = requests.get(URL)
    print(response.status_code)
    print(response.json())

def test_post():
    print("test_post")
    data = {"string": "aaa", "lists": [0.2, 0.3]}
    response = requests.post("{}/post/test".format(URL), json=data)
    print(response.status_code)
    print(response.json())

def test_log_extract():
    print("test_log_extract")
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
    df = pandas.read_csv("dev_data/log_processed_2020-08-13.csv", dtype=DTYPE_2)
    data = {
        "ymd": "2020-08-13",
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
    print(response.status_code)
    #print(response.json())

if __name__ == "__main__":
    test_connect()
    test_post()
    test_log_extract()
