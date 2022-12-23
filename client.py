import logging
from threading import Thread

from mqtt import MQTTAdapter


class MQTTTelnetClient(Thread):
    SUBSCRIBE_COMMAND = 'subscribe'
    POLL_COMMAND = 'poll'
    QUIT_COMMAND = 'quit'

    def __init__(self, address, sock, mqtt: MQTTAdapter, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.address = address
        self.sock = sock
        self.mqtt = mqtt
        self._running = True

        self.pending_subscriptions = []
        self.active_subscriptions = []

    def run(self):
        while self._running:
            data = self.sock.recv(1024)
            if not data:
                break
            message = data.decode().strip()

            if message == self.QUIT_COMMAND:
                break
            elif message.startswith(self.SUBSCRIBE_COMMAND):
                try:
                    topic_to_subscribe = message.split()[1]
                    self._subscribe(topic_to_subscribe)
                except IndexError:
                    self.send_message('You must provide a topic as argument')
            elif message == self.POLL_COMMAND:
                self._start_polling()

        self.terminate()

    def send_message(self, message):
        self.sock.send(f'{message}\r\n'.encode())

    def _subscribe(self, topic_to_subscribe):
        callback = lambda topic, message: self.send_message(f'{topic}: {message}')
        self.pending_subscriptions.append((topic_to_subscribe, callback))
        logging.info(f'Client {self.address} subscribed to {topic_to_subscribe}')

    def terminate(self):
        self._running = False
        for topic, callback in self.active_subscriptions:
            self.mqtt.unsubscribe(topic, callback)

        self.sock.shutdown(2)
        self.sock.close()

        logging.info(f'Client {self.address} disconnected')

    def _start_polling(self):
        for topic, callback in self.pending_subscriptions:
            self.mqtt.subscribe(topic, callback)
        self.active_subscriptions = self.pending_subscriptions
        self.pending_subscriptions = []
        logging.info(f'Client {self.address} started polling')


class ClientFactory:
    def __init__(self, mqtt_adapter: MQTTAdapter):
        self.mqtt_adapter = mqtt_adapter

    def create_client(self, conn, addr):
        return MQTTTelnetClient(addr, conn, self.mqtt_adapter)
