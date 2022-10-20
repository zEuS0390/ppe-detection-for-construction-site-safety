from src.camera import Camera
from src.client import MQTTClient
from src.detection import Detection
from torch import no_grad
import argparse, configparser, threading, time, json

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
		- LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

@no_grad()
def func(cam, det, mqtt_client: MQTTClient):
    while cam.cap.isOpened():
        processed = cam.getFrame()
        if processed is not None:
            result = det.detect(processed, cam.frame)
            if len(result["detected"]):
                payload = json.dumps(result)
                mqtt_client.client.publish(mqtt_client.topic, payload=payload)
            cam.det = result

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    confparser = configparser.ConfigParser()
    confparser.read("./cfg/config.ini")
    mqtt_client = MQTTClient(
        client_id = confparser.get("mqtt_notif", "client_id_name"),
        topic = confparser.get("mqtt_notif", "topic_name"),
        broker = confparser.get("mqtt_notif", "broker_ip")
    )
    det = Detection(confparser)
    cam = Camera()
    detThread = threading.Thread(target=func, args=(cam, det, mqtt_client))
    detThread.start()
    
