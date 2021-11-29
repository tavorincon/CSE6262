from fastapi import FastAPI
from fbprophet import Prophet
import pickle
import pandas as pd 
import datetime
import json

app = FastAPI()

model_path = 'time_series.pkl'

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

@app.get('/')
def get_root():

	return {'message': 'Welcome to the crime prediction API'}

@app.get('/predict_crime/')
async def crime_prediction(per: int, freq: str):
	return predict_crime(model, per, freq)
