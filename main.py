from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import dotenv
import os

import datetime
import pickle
import pandas as pd
import mysql.connector
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
import pdb

# Load dotenv
dotenv.load_dotenv()


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#################################################################################
# Model Functions
################################################################################

model_path = '/app/time_series.pkl'

with open(model_path,"rb") as f:
	model = pickle.load(f)

def predict_crime(model, period, frequency):

    TODAY = datetime.date.today()

    dates = pd.date_range(start=TODAY, periods=period, freq=frequency)
    df = pd.DataFrame({"ds": dates})
    forecast = model.predict(df)

    # return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()


    #results = [{str(ds): {'date': ds, 'prediction': yhat}} for (ds, yhat) in forecast[['ds', 'yhat']]]

    return forecast

#################################################################################
# Database Functions
################################################################################

def crime_prediction_data(frequency, nodays = 30):

    start_date = datetime.date(2021, 12, 1)
    end_date = start_date + datetime.timedelta(days=nodays)

    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'crime_db'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(f'SELECT ds, yhat, zip_code FROM {frequency} WHERE ds BETWEEN \'{start_date}\' AND \'{end_date}\'')
    results = [{str(ds): {'zip_code': zip_code, 'prediction': yhat}} for (ds, yhat, zip_code) in cursor]
    cursor.close()
    connection.close()

    return results

def crime_prediction_data_bytype(frequency, nodays = 30):

    start_date = datetime.date(2021, 12, 1)
    end_date = start_date + datetime.timedelta(days=nodays)

    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'crime_db'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute(f'SELECT ds, yhat, zip_code, IBRS FROM {frequency}_bytype WHERE ds BETWEEN \'{start_date}\' AND \'{end_date}\'')
    results = [{str(ds): {'zip_code': zip_code, 'prediction': yhat, 'crime_type': IBRS}} for (ds, yhat, zip_code, IBRS) in cursor]
    cursor.close()
    connection.close()

    return results

#################################################################################
# API Functions
#################################################################################


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/historical-crime")
async def historical_data(year: int):

#    pdb.set_trace()

    db_connection_str = 'mysql+pymysql://root:root@db:3306/crime_db'
    db_connection = create_engine(db_connection_str)
    df = pd.read_sql(f'SELECT * FROM crime_db.historical_crime WHERE year(datetime) = {year}', con=db_connection)
    
    results = df.to_csv(index=False)

    return Response(content=results, media_type="text/csv")



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

@app.get('/predict_crime/', response_class=JSONResponse)
async def crime_prediction(per: int, freq: str):
	#return JSONResponse(content=predict_crime(model, per, freq))
    return predict_crime(model, per, freq)


@app.get('/get_crime_data/')
async def get_crime_prediction_data(freq: str, days: int):
#async def index():
	return JSONResponse(content=crime_prediction_data(freq))

@app.get('/get_crime_data_bytype/')
async def get_crime_prediction_data_bytype(freq: str, days: int):
#async def index():
	return JSONResponse(content=crime_prediction_data_bytype(freq))


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
