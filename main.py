from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/foo")
def read_item():
    return {"test": "foo"}

@app.get("/foo")
def read_item():
    return {"test": "bar"}