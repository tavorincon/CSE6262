FROM python:3.7

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Install dev & build packages
#RUN yum install python3-dev build-essential -y

# Install deps now to avoid misleading error messages which are actually non-errors at the next step
RUN pip3 install convertdate==2.1.2 lunarcalendar==0.0.9 holidays==0.10.3 cython==0.29.21 pystan==2.19.1.1 pandas==1.3.3 plotly

# Install/build Prophet
RUN pip3 install fbprophet==0.6

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]

