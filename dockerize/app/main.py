from fastapi import FastAPI
from fbprophet import Prophet
import pickle
import pandas as pd 
import datetime
import json
import mysql.connector


#PATH_TO_MODELS_DIR = Path('.')

app = FastAPI()

model_path = '/code/app/time_series.pkl'

with open(model_path,"rb") as f:
	model = pickle.load(f)


def predict_crime(model, period, frequency):

	TODAY = datetime.date.today()

	dates = pd.date_range(start=TODAY, periods=period, freq=frequency)
	df = pd.DataFrame({"ds": dates})
	forecast = model.predict(df)

	# return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

	result = forecast.to_json(orient="index")
	parsed = json.loads(result)
	 
	return json.dumps(parsed, indent=4) 

def crime_prediction_data(frequency):
	config = {
		'user': 'root',
		'password': 'root',
		'host': 'db',
		'port': '3306',
		'database': 'crime_db'
    }
	connection = mysql.connector.connect(**config)
	cursor = connection.cursor()
	cursor.execute('SELECT ds, yhat, zip_code FROM', frequency)
	results = [{zip_code: yhat} for (ds, yhat, zip_code) in cursor]
	cursor.close()
	connection.close()

	return results


@app.get('/')
def get_root():

	return {'message': 'Welcome to the crime prediction API'}

@app.get('/predict_crime/')
async def crime_prediction(per: int, freq: str):
	return predict_crime(model, per, freq)


@app.get('/get_crime_data/')
async def get_crime_prediction_data(freq: str):
#async def index():
	return json.dumps({'crime_data': crime_prediction_data(freq)})


