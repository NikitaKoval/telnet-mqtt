# Telnet MQTT client

## Problem
Create server that helps communicate telnet clients with MQTT

## How to run the server
## Dockerized
```shell
docker-compose build server
docker-compose up
```

## Manual

Download and install [Eclipse Mosquitto](https://mosquitto.org) first

### Install requirements
```shell
pip install -r requirements.txt
```

### Run the server
```shell
python main.py
```

Optionally you can specify `MQTT_HOST` and `MQTT_PORT` environment variables.

# How to test
In command line run
```shell
telnet localhost 1234

subscribe test/123 # To subscribe to the topic
subscribe test/234 # To subscribe to the topic

poll # To start polling messages

quit # To disconnect from the server
```

