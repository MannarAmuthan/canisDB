FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY Pipfile .
COPY Pipfile.lock .

EXPOSE 5003 5012 5022

RUN pip3 install pipenv
RUN pipenv requirements > deploy-requirements.txt
RUN pip install -r deploy-requirements.txt

COPY src/ .

COPY config.json .