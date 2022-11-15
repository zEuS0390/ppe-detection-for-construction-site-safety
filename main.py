from src.db.database import DatabaseHandler
from src.db.crud import *
from src.db.tables import *
from sqlalchemy import select
from src.client import MQTTClient
from src.detection import Detection
from src.utils import checkLatestWeights
from src.recognition import Recognition
from src.camera import Camera
import configparser, time

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
        - LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

def main():

    # Check latest weights file
    checkLatestWeights()

    # Load app configuration file
    cfg = configparser.ConfigParser()
    cfg.read("./cfg/app.cfg")

    # Instantiate objects
    database = DatabaseHandler(cfg=cfg)
    mqtt_notif = MQTTClient("notif")
    mqtt_set = MQTTClient("set")
    recognition = Recognition(cfg)
    camera = Camera(cfg)
    insertPersons(database, cfg.get("face_recognition", "persons"))
    insertPPEClasses(database, cfg.get("yolor","classes"))
    detection = Detection(cfg, database, camera, recognition, mqtt_notif, mqtt_set)

    # Start threads
    mqtt_notif.start()
    mqtt_set.start()
    camera.start()
    detection.start()

    try:
        while True: time.sleep(1)
    except:
        detection.isRunning = False
        camera.isRunning = False

if __name__=="__main__":
    main()