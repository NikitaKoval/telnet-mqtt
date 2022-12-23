import itertools
from threading import Lock

from paho.mqtt import client as mqtt
from paho.mqtt.client import topic_matches_sub


class MQTTAdapter:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.subscriptions = {}

        self.client = None
        self.lock = Lock()

    def connect(self):
        self.client = mqtt.Client('mqtt_client')
        self.client.connect(self.host, self.port)
        self.client.on_message = self._on_message
        self.client.loop_start()

    def _on_message(self, client, userdata, msg):
        topic = msg.topic

        callbacks_to_call = itertools.chain(*[
            callbacks for subscribe_topic, callbacks in self.subscriptions.items()
            if topic_matches_sub(subscribe_topic, topic)
        ])
        for callback in callbacks_to_call:
            callback(topic, msg.payload.decode())

    def subscribe(self, topic: str, callback):
        self.lock.acquire()
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []

        self.subscriptions[topic].append(callback)

        self.client.subscribe(topic)
        self.lock.release()

    def unsubscribe(self, topic, callback):
        self.lock.acquire()
        self.subscriptions[topic] = list(filter(lambda x: x != callback, self.subscriptions[topic]))
        self.lock.release()
