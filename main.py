from src.client import MQTTClient
from src.detection import Detection, detThreadFunc
from src.utils import checkLatestWeights
from src.recognition import Recognition
from src.camera import Camera
import configparser, threading

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

    # Check latest weights file
    checkLatestWeights()

    # Load app configuration file
    cfg = configparser.ConfigParser()
    cfg.read("./cfg/app.cfg")

    # Instantiate objects
    det = Detection(cfg)
    rec = Recognition(cfg)
    mqtt_notif = MQTTClient("notif")
    mqtt_camera = MQTTClient("camera")
    cam = Camera(mqtt_camera)
    
    # Start threads
    mqtt_notif.start()
    mqtt_camera.start()
    cam.start()
    det.start(cam, detThreadFunc, rec, mqtt_notif)
