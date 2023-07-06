from paho.mqtt.client import Client, connack_string
from src.utils import parsePlainConfig
import time, os, shutil, logging, ssl, json

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
        self.auth_cert = auth_cert
        if not self.auth_cert:
            # Uses username and password authentication
            missing = False
            for key, value in args.items():
                if value == None:
                    print(f"[MQTTClient]: Missing MQTT client argument: {key}")
                    self.logger.error(f"[MQTTClient]: Missing MQTT client argument: {key}")
                    missing = True
            if missing:
                raise Exception("[MQTTClient]: Missing MQTT client argument(s)")
            self.client_id = args['client_id']
            self.pub_topic = args['pub_topic']
            self.sub_topic = args['sub_topic']
            self.hostname = args['hostname']
            self.username = args['username']
            self.password = args['password']
            self.port = int(args['port'])
            self.client = Client(client_id=self.client_id)
            self.client.username_pw_set(self.username, self.password)
        else:
            # This means the authentication method is through certificate
            self.hostname = args['hostname']
            self.port = int(args['port'])
            self.pub_topic = args['pub_topic']
            self.sub_topic = args['sub_topic']
            self.client_id = args['client_id']
            self.ca_certs = args['ca_certs']
            self.certfile = args['certfile']
            self.keyfile = args['keyfile']
            missing = False
            for key, value in args.items():
                if value == None:
                    print(f"[MQTTClient]: Missing MQTT client argument: {key}")
                    self.logger.error(f"[MQTTClient]: Missing MQTT client argument: {key}")
                    missing = True
            if missing:
                raise Exception("[MQTTClient]: Missing MQTT client argument(s)")
            self.client = Client(client_id=self.client_id)
            self.client.tls_set(
                ca_certs=self.ca_certs,
                certfile=self.certfile,
                keyfile=self.keyfile,
                tls_version=ssl.PROTOCOL_SSLv23
            )
            self.client.tls_insecure_set(True)
        self.client.on_connect = self.on_connect
        self.is_connected = False
        
    def start(self):
        while True:
            try:
                print(f"[MQTTClient]: Connecting...")
                self.client.connect(
                    self.hostname,
                    self.port,
                )
                break
            except Exception as e:
                print(f"[MQTTClient]: {e}")
                self.logger.error(f"[MQTTClient]: {e}")
            time.sleep(1)
        self.client.loop_start()

    def stop(self):
        self.is_connected = False
        self.client.disconnect()
        self.client.loop_stop()

    def __del__(self):
        self.is_connected = False
        self.client.disconnect()
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connection result: {connack_string(rc)}")
        print(f"Connection result: {connack_string(rc)}")
        if rc == 0:
            self.is_connected = True
            # client.publish(self.pub_topic, payload=json.dumps({"message": "zeus"}), qos=0, retain=False)
            # self.client.subscribe(self.sub_topic)
            # print(f"Client subscribe to {self.sub_topic}")
        elif rc == 5:
            # Not authorized (incorrect username or password)
            print("Not authorized (incorrect credentials)")
            pass

    def publish(self, payload):
        self.client.publish(
                self.pub_topic, 
                payload=payload
        )
        print(f"Client published to {self.pub_topic}")
