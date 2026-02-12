from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from request import fetch_species

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="templates")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Species API
@app.get("/species")
def species_api(name: str = Query(...)):
    data = fetch_species(name)
    return data

# Status route
@app.get("/status")
def status():
    return {"message": "Server is running!"}
