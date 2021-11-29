# https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi
# docker build -t cse6242 .
# docker run -d --name cse6242-app -p 8000:80 cse6242


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt


# For development purposes not needed
# COPY ./ /app