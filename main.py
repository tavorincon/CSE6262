from typing import Optional

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import dotenv
import os

# Load dotenv
dotenv.load_dotenv()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/historical-crime")
# Agregar filtro por fecha y el default seria un año hacia atras (para el mapa 3D por hexagono)
async def historical_data(days: Optional[int] = 365):
    # Cambiar el CSV por el query
    with open("data/crime/test_latlon.csv", 'r') as f:
        return f.read()

@app.get("/officer-allocation")
# Regresa la predicción del numero de crimenes y la asignación propuesta de oficiales (para pintar el mapa por zipcode)
async def historical_data(days: Optional[int] = 365):
    # Cambiar el CSV por el query
    return None

@app.get("/crime-prediction")
# Regresa la predicción del numero de crimenes y la asignación propuesta de oficiales (para pintar el timeseries por zipcode en el hover)
async def historical_data(zip_code: str):
    # Cambiar el CSV por el query
    return None

################################################################################
# Front End
################################################################################
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/allocation", response_class=HTMLResponse)
async def show_map(request: Request):
    return templates.TemplateResponse(
        "allocation.html",
        {"request": request, "segment": "allocation", "mapbox_key": os.getenv("MAPBOX_KEY")},
    )


@app.get("/historical", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "historical.html",
        {"request": request,
        "segment": "historical"},
    )

@app.get("/dash", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request,
        "segment": "index"},
    )

app.mount("/app", StaticFiles(directory="frontend/app"), name="app")
