FROM python:3.9-slim

ENV PYTHONUNBUFFERED True 

RUN apt update
RUN apt install -y libgl1 libglib2.0-0 libsm6 libxrender1 libxext6

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install tensorflow-cpu

COPY func.py .

CMD python -m parliament func.py