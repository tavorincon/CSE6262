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
import numpy as np
from ortools.linear_solver import pywraplp
import mysql.connector

from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
import pdb

from optimization_model import assign_officers, generate_geojson

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

config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'crime_db'
    }
#################################################################################
# Model Functions
################################################################################

model_path = './time_series.pkl'

#with open(model_path,"rb") as f:
	#model = pickle.load(f)

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
# Returns the precition of crimes and the proposed officer allocation (to paint the map by zipcode)
# Example /officer-allocation?type=weekly&start_date=2021-12-05&crime_type=all&number_of_officers=700
async def historical_data(type: str, start_date: str, crime_type: str, number_of_officers: int):
    table_name = "weekly"
    if(type == 'month'):
        table_name = 'monthly'

    filter_qry = ""
    if(crime_type != 'All'):
        filter_qry = f"AND IBRS = '{crime_type}'"

    #### DATASETS ####
    #Read in population_data data
    population_data = pd.read_csv("./data/map/population.csv")
    population_data['Population'] = population_data['Population'].str.replace(',', '').astype(int)
    population_data = population_data[population_data['City'].str.contains('Kansas City')]
    population_data.drop(['Location', 'City', 'People / Sq. Mile', 'National Rank'], axis=1, inplace=True)

    #Read in forecast data
    connection = mysql.connector.connect(**config)
    query1 = """SELECT zip_code, SUM(yhat) AS yhat FROM crime_db.%s_crime_bytype
    WHERE ds = '%s' GROUP BY zip_code
    """ %(table_name, start_date)
    forecast_data = pd.read_sql(query1, connection)

    #Read in forecast data (filtered by crime type)
    if(crime_type != 'All'):
        query1 = """SELECT zip_code, SUM(yhat) AS yhat FROM crime_db.daily_crime_bytype
        WHERE ds = '%s' %s GROUP BY zip_code
        """ %(start_date, filter_qry)
        filtered_by_crime_data = pd.read_sql(query1, connection)
    else:
        filtered_by_crime_data = forecast_data.copy()

    #Read in historical crime data
    query2 = """SELECT zip_code,
    (SUM(
        IF( `Firearm Used Flag` IN ('Y', 'True', 1) , 1, 0)
    ) / COUNT(*)) AS 'FireArmProportion'
    FROM crime_db.historical_crime
    WHERE YEAR(`datetime`) = 2020
    GROUP BY zip_code
    ORDER BY 2 DESC
    """
    # -- WHERE `datetime` BETWEEN '2020-12-01' AND '2020-12-08'
    # -- WHERE `datetime` > '2021-09-08'
    firearm_data = pd.read_sql(query2, connection)
    firearm_data["zip_code"] = firearm_data["zip_code"].astype('int64')


    connection.close()

    total_crimes = sum(forecast_data['yhat'])

    #Get Officer assignments
    final_results = assign_officers(total_crimes, number_of_officers, population_data, firearm_data, forecast_data, type)

    # If final_results is string, then there was an error
    if(isinstance(final_results, str)):
        return {'error': final_results}

    return generate_geojson(final_results, filtered_by_crime_data, clean_map=True)


@app.get("/crime-prediction")
# Returns the daily crime prediction by zipcode
async def historical_data(zip_code: str, start: str, crime_type: str):
    filter_qry = ""
    if(crime_type != 'All'):
        filter_qry = f"AND IBRS = '{crime_type}'"

    query = """
    SELECT ds AS x, SUM(yhat) AS y FROM daily_crime_bytype dcb
    WHERE ds BETWEEN '{}' AND DATE_ADD('{}', INTERVAL 30 DAY)
    AND zip_code = {} {}
    GROUP BY ds
    ORDER BY ds DESC
    """.format(start, start, zip_code, filter_qry)
    connection = mysql.connector.connect(**config)
    data = pd.read_sql(query, connection)
    connection.close()

    return Response(content=data.to_json(orient='records'), media_type="application/json")

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
    # Future work. Get the data from the official police system
    police_officers = 704

    # Get improvement in crime rate
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
    1 - (SELECT
    COUNT(*)
    FROM historical_crime hc
    WHERE `datetime` BETWEEN DATE_SUB(CURDATE(), INTERVAL 2 MONTH) AND DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    ) / (
    SELECT
    COUNT(*)
    FROM historical_crime hc
    WHERE `datetime` BETWEEN DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND DATE_SUB(CURDATE(), INTERVAL 2 MONTH)
    ) AS p_reduction
    """)
    p_reduction = round(100 * cursor.fetchone()[0], 1)
    cursor.close()

    # Polices by population
    population_data = pd.read_csv("data/map/population.csv")
    population_data['Population'] = population_data['Population'].str.replace(',', '').astype(int)
    population_data = population_data[population_data['City'].str.contains('Kansas City')]
    total_population = population_data['Population'].sum()

    officers_per10k = round(police_officers / (total_population / 10000), 1)

    # Firearm usage
    cursor = connection.cursor()
    cursor.execute("""
    SELECT
    (SUM(
        IF( `Firearm Used Flag` IN ('Y', 'True', 1) , 1, 0)
    ) / COUNT(*)) AS 'FireArmProportion'
    FROM crime_db.historical_crime
    WHERE `datetime` > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    """)
    firearm_p = round(100 * cursor.fetchone()[0], 1)
    cursor.close()

    # Time series for crime
    ts = pd.read_sql_query("""
    SELECT DATE_FORMAT(`datetime`,'%Y-%m') AS ym,
    SUM(
        IF( `Firearm Used Flag` IN ('Y', 'True', 1) , 1, 0)
    ) AS 'WithFireArm',
    SUM(
        IF( `Firearm Used Flag` NOT IN ('Y', 'True', 1) , 1, 0)
    ) AS 'WithoutFireArm'
    FROM crime_db.historical_crime
    WHERE `datetime` > DATE_SUB(CURDATE(), INTERVAL 9 MONTH)
    GROUP BY DATE_FORMAT(`datetime`,'%Y-%m')
    ORDER BY 1
    """, connection)

    with_firearm = ",".join(list(ts['WithFireArm'].astype(int).astype(str)))
    without_firearm = ",".join(list(ts['WithoutFireArm'].astype(int).astype(str)))

    connection.close()



    return templates.TemplateResponse(
        "index.html",
        {"request": request,
        "segment": "index",
        "p_reduction": p_reduction,
        "officers_per10k": officers_per10k,
        "firearm_p": firearm_p,
        "police_officers": police_officers,
        "with_firearm": with_firearm,
        "without_firearm": without_firearm
        },
    )

app.mount("/app", StaticFiles(directory="frontend/app"), name="app")
