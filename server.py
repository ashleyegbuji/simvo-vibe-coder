from fastapi import FastAPI, Query
from request import fetch_species

app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}

@app.get("/species")
def get_species(name: str = Query(..., description="Name of the species")):
    print("i got: " + search)
    return fetch_species(name, per_page)