import logging
import signal
import sys
import os

from client import ClientFactory
from mqtt import MQTTAdapter
from server import Server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

HOST = '0.0.0.0'
PORT = 1234

MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_HOST = os.environ.get('MQTT_HOST', 'localhost')

if __name__ == '__main__':
    mqtt_adapter = MQTTAdapter(MQTT_HOST, MQTT_PORT)
    client_factory = ClientFactory(mqtt_adapter)
    server = Server(HOST, PORT, client_factory)

    def signal_handler(signum, frame):
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    mqtt_adapter.connect()
    server.run()
