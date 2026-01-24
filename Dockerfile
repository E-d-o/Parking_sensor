
FROM balenalib/raspberry-pi-python:3.11

WORKDIR /app

COPY requirements.txt .


RUN apt update && apt install -y \
    gcc\
    libc6-dev\
    make 
RUN pip install -r requirements.txt


CMD ["python3", "/app/src/basic_proximity_sensor.py"]