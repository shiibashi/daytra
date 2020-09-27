from fastapi import FastAPI
from starlette.requests import Request
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title='RLBOTTER', description='RLBOTTER', version='1')
 

class TestData(BaseModel):
    string: str
    lists: List[float]

class ProdData(BaseModel):
    pass

@app.get("/")
def index(request: Request):
    return {'connect': 'OK'}

@app.post("/post/test")
def post_test(data: TestData):
    return {"request_data": {"string": data.string, "lists": data.lists}}
