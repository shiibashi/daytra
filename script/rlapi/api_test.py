import requests
from pydantic import BaseModel

URL = "http://127.0.0.1:8000"

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

if __name__ == "__main__":
    test_connect()
    test_post()
