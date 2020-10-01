import requests
from pydantic import BaseModel
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

if __name__ == "__main__":
    test_connect()
    test_post()
