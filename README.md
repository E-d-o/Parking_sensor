# Parking_sensor

A raspberry pi project for Iot course at the University of Udine.

# Installation

In order to install the project, Docker is required.

## Installation steps

Follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/E-d-o/Parking_sensor.git
    ```

2. Navigate to the project directory:

    ```bash
    cd parking_sensor
    ```

3. Run docker compose:

    ```bash
    docker compose up -d
    ```

4. Check if the containers are running:

    ```bash
    docker ps
    ```

You should see three containers running: grafana, influxdb, and parking_sensor-sensor_script.

5. To stop the project:

    ```bash
    docker compose down
    ```

## Installation as service

To install the project as a systemd service:

1. Make sure you are in the project directory:

    ```bash
    cd parking_sensor
    ```

2. Copy the service file to the systemd directory

```bash
sudo cp parking_sensor.service /etc/systemd/system/
```

3. Enable and start the service:

```bash
sudo systemctl enable parking_sensor.service
sudo systemctl start parking_sensor.service
```

4. Check the status of the service:

```bash
sudo systemctl status parking_sensor.service
```

If the output shows that the service is enabled and active, the installation was successful.

5. To stop the service:

```bash
sudo systemctl stop parking_sensor.service
```

# Usage

You can access the dashboard by visiting http://localhost:3000 in your web browser (replace localhost with the IP address of your Raspberry Pi if you are accessing it remotely).
There Grafana will ask you to input the username and password, the default credentials are specified in the .env file, which are `admin` and `admin`.

# Changing the default credentials

You can change the default credentials by editing the .env file and changing the values of the admin credentials and also the InfluxDB token.
