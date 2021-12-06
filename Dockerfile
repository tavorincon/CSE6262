# https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi
# docker build -t cse6242 .
# docker run -d --name cse6242-app -p 8000:80 cse6242


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install deps now to avoid misleading error messages which are actually non-errors at the next step
RUN pip3 install convertdate==2.1.2 lunarcalendar==0.0.9 holidays==0.10.3 cython==0.29.21 pystan==2.19.1.1 pandas==1.3.3 plotly

# Install/build Prophet
RUN pip3 install fbprophet==0.6
RUN pip3 install pymysql
RUN pip3 install ortools

# For development purposes not needed
# COPY ./ /app