FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN pip install --upgrade pip

RUN apk update \
    && apk add gcc python3-dev postgresql-dev

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app