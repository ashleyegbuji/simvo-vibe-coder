from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from request import fetch_species_data

app = FastAPI()

# CORS (important for frontend calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


@app.get("/hello")
async def read_hello():
    return {"message": "hello"}


@app.get("/species")
async def get_species(name: str):
    data = await fetch_species_data(name)
    return {"data": data}


@app.get("/", response_class=FileResponse)
async def return_site():
    return FileResponse(
        BASE_DIR / "templates" / "index.html",
        media_type="text/html"
    )


