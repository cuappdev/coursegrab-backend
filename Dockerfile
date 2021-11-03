FROM python:3.8

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000
CMD python src/manage.py db upgrade; python src/run.py
