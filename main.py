from src.camera import Camera
from src.client import MQTTClient, streamCamera
from src.detection import Detection, detThreadFunc
import configparser
import threading

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
	    - LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

if __name__=="__main__":

    # Load app configuration file
    cfg = configparser.ConfigParser()
    cfg.read("./cfg/config.ini")

    # Instantiate objects
    mqtt_notif = MQTTClient(cfg, "mqtt_notif")
    mqtt_camera = MQTTClient(cfg, "mqtt_camera")
    cam = Camera()
    mqtt_camera_thread = threading.Thread(
        target=streamCamera, 
        args=(cam, mqtt_camera)
    )
    det = Detection(cfg)
    
    # Start threads
    mqtt_notif.start()
    mqtt_camera.start()
    cam.start()
    mqtt_camera_thread.start()
    det.start(cam, detThreadFunc, mqtt_notif)
