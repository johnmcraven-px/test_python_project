from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/foo")
def read_item_foo():
    return {"test": "foo"}

@app.get("/bar")
def read_item_bar():
    return {"test": "bar"}