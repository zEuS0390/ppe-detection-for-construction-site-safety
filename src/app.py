from src.db.database import DatabaseHandler
from src.db.crud import *
from src.db.tables import *
from sqlalchemy import select
from src.client import MQTTClient
from src.detection import Detection
from src.utils import checkLatestWeights
from src.recognition import Recognition
from src.camera import Camera
from src.hardware import Hardware
import configparser, time

class Application:

    @staticmethod
    def main():
       
        # Load app configuration file
        cfg = configparser.ConfigParser()
        cfg.read("./cfg/app.cfg")

        hardware = Hardware(cfg)
        
        hardware.ledControl.setColor(False, False, True)

        # Check latest weights file
        checkLatestWeights()

        hardware.ledControl.setColor(True, True, False)
        hardware.buzzerControl.play(1, 0.05, 0.05)

        # Instantiate objects
        database = DatabaseHandler(cfg=cfg)
        mqtt_notif = MQTTClient("notif")
        mqtt_set = MQTTClient("set")
        recognition = Recognition(cfg)
        camera = Camera(cfg)
        insertPersons(database, cfg.get("face_recognition", "persons"))
        insertPPEClasses(database, cfg.get("yolor","classes"))
        detection = Detection(cfg, database, camera, recognition, mqtt_notif, mqtt_set)

        hardware.ledControl.setColor(False, False, False)
        hardware.buzzerControl.play(1, 0.05, 0.05)

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

        hardware.ledControl.setColor(True, False, False)
        hardware.buzzerControl.play(5, 0.05, 0.05)
        hardware.ledControl.setColor(False, False, False)
