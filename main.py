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


################################################################################
# Front End
################################################################################
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/map", response_class=HTMLResponse)
async def show_map(request: Request):
    return templates.TemplateResponse(
        "sample-choroplet.html",
        {"request": request, "mapbox_key": os.getenv("MAPBOX_KEY")},
    )


app.mount("/app", StaticFiles(directory="frontend/app"), name="app")
