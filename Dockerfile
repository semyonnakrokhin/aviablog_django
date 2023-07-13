# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .



RUN apt-get update 
RUN apt-get -y install libpq-dev gcc

RUN pip install -r requirements.txt


# copy project
COPY . .


# run commands
#CMD sh -c "python manage.py migrate && python manage.py loaddata fixture.json && python manage.py runserver 0.0.0.0:8000"
