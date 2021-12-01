import numpy as np 
import os 
import pandas as pd 
import datetime
import glob
import csv
import datetime
from datetime import datetime
from matplotlib import pyplot
from fbprophet import Prophet
import matplotlib.pyplot as plt


#last 6 years
year = datetime.today().year
YEARS = [year - i for i in range(11)]

colnames=['Reported_Date'] 
col_list = ['Reported_Date']
types_dict = { 'Reported_Date': str,'Reported_Time': str, 'From_Date': str, 'From_Time': str,'To_Date': str, 'Offense': str, 'IBRS': str, 'Description': str, 'Beat': str, 'Address': str, 'City': str, 'Zip Code': str, 'Area' : str, 'DVFlag' : str, 'Involvement' : str, 'Race': str, 'Sex': str, 'Age': int, 'Firearm Used Flag': str}
#path = r'data' 
all_files = glob.glob("/KCPD_Crime_Data_2021.csv")

li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, usecols=col_list, header=0, na_values = "not available")
    print(filename)
    li.append(df)
frame = pd.concat(li, axis=0, ignore_index=True)
frame['Reported_Date'] = pd.to_datetime(frame['Reported_Date'])

frame.sort_values(by=['Reported_Date'])
#df2 = frame.groupby(by=['Reported_Date'],dropna=False).sum()
df = frame.groupby('Reported_Date')['Reported_Date'].count().rename('Total_Crimes').reset_index()

df.columns = ['ds', 'y']

df.index = pd.to_datetime(df['ds'])

#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
df_Month =  df.resample('M').sum().reset_index() ##df2 = df.groupby(pd.Grouper(freq='M')).sum().reset_index()
df_Week =  df.resample('W').sum().reset_index()

df_Week

# Python
m = Prophet(daily_seasonality=True) #changepoint.prior.scale = 0.5
m.fit(df_Week)

future = m.make_future_dataframe(periods=52, freq='W') #future_air=model_air.make_future_dataframe(periods=12, freq='M')
future.tail()

# Python
forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()