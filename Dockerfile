
FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt


CMD ["python3", "/app/src/basic_proximity_sensor.py"]