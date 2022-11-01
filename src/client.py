from paho.mqtt.client import Client, connack_string
from configparser import ConfigParser
from src.utils import imageToBinary
import time, json

class MQTTClient:

    def __init__(self, cfg: ConfigParser, cfg_section: str, on_message=None, port=1883):
        self.client_id = cfg.get(cfg_section, "client_id_name")
        self.topic = cfg.get(cfg_section, "topic_name")
        self.broker = cfg.get(cfg_section, "broker_ip")
        self.port = port
        self.client = Client(client_id=self.client_id)
        self.client.username_pw_set(cfg.get(cfg_section, "username"), cfg.get(cfg_section, "password"))
        self.client.on_connect = self.on_connect
        if on_message is not None:
            self.client.on_message = on_message
        
    def start(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def __del__(self):
        self.client.disconnect()
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connection result: {connack_string(rc)}")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload}")

def streamCamera(cam, mqtt: MQTTClient):
    while True:
        if cam.frame is not None:
            img = imageToBinary(cam.frame)
            payload = json.dumps({"image": img, "detected": []})
            mqtt.client.publish("rpi/camera", payload)
        time.sleep(0.03)
