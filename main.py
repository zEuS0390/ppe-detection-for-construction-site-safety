from src import *
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

@torch.no_grad()
def func(cam, det, mqtt_client: MQTTClient):
    while True:
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
    confparser.read("./config.cfg")
    mqtt_client = MQTTClient(
        client_id = "rpi-camera-1",
        topic = "rpi/notif",
        broker = "192.168.1.14"
    )
    det = Detection(confparser)
    cam = Camera()
    time.sleep(10)
    detThread = threading.Thread(target=func, args=(cam, det, mqtt_client))
    detThread.start()
    
