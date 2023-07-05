from paho.mqtt.client import Client, connack_string
from src.utils import parsePlainConfig
import time, os, shutil, logging

class MQTTClient:

    """
    Methods:
        - start         ()
        - stop          ()
        - on_connect    (client: any, 
                         user: any, 
                         flag: any, 
                         rc: any)
        - publish       (payload: any)
    """

    def __init__(self, args: dict, auth_cert=False):
        self.logger = logging.getLogger()
        if not auth_cert:
            for key, value in args.items():
                if value == None:
                    self.logger.error("[MQTTClient]: Missing MQTT client argument(s)")
                    raise Exception("[MQTTClient]: Missing MQTT client argument(s)")
            self.client_id = args['client_id']
            self.topic = args['topic']
            self.hostname = args['hostname']
            self.username = args['username']
            self.password = args['password']
            self.port = int(args['port'])
            self.client = Client(client_id=self.client_id)
            self.client.username_pw_set(self.username, self.password)
        else:
            # This means the authentication method is through certificate
            pass
        self.client.on_connect = self.on_connect
        
    def start(self):
        while True:
            try:
                self.client.connect(self.hostname, self.port)
                break
            except Exception as e:
                self.logger.error(f"[MQTTClient]: {e}")
            time.sleep(1)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()

    def __del__(self):
        self.client.disconnect()
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connection result: {connack_string(rc)}")
        if rc == 0:
            self.client.subscribe(self.topic)
        elif rc == 5:
            # Not authorized (incorrect username or password)
            pass

    def publish(self, payload):
        self.client.publish(self.topic, payload=payload)
