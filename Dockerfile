FROM python:3.8-slim-buster

COPY ./weatherAggregator /app/weatherAggregator
COPY setup.py /app/
COPY MANIFEST.in /app/
COPY ./instance/start_db.sqlite /app/instance/

WORKDIR /app

RUN python -m pip install .
EXPOSE 5000
ENTRYPOINT ["flask"]