from paho.mqtt.client import Client, connack_string

class MQTTClient:

    def __init__(self, client_id, topic, broker, port=1883):
        self.client_id = client_id
        self.topic = topic
        self.broker = broker
        self.port = port
        self.client = Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def __del__(self):
        self.client.disconnect()
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connection result: {connack_string(rc)}")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload}")