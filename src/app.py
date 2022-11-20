from src.db.database import DatabaseHandler
from src.db.crud import *
from src.db.tables import *
from sqlalchemy import select
from src.client import MQTTClient
from src.detection import Detection
from src.utils import getLatestFiles, getRecognitionData
from src.recognition import Recognition
from src.camera import Camera
from src.hardware import Hardware
import os, glob, configparser, time

class Application:

    @staticmethod
    def main():
       
        # Load app configuration file
        cfg = configparser.ConfigParser()
        cfg.read("./cfg/app.cfg")

        hardware = Hardware(cfg)

        hardware.ledControl.setColor(False, False, True)

        getLatestFiles(cfg_name="face_recognition", target_names=["face_recognition", "detection"])
        recognition = getRecognitionData(cfg)

        hardware.ledControl.setColor(True, True, False)
        hardware.buzzerControl.play(1, 0.05, 0.05)

        # Instantiate objects
        database = DatabaseHandler(cfg=cfg)
        insertPersons(database, recognition["info"])
        insertPPEClasses(database, cfg.get("yolor","classes"))

        mqtt_notif = MQTTClient("notif")
        mqtt_set = MQTTClient("set")
        recognition = Recognition(cfg)
        camera = Camera(cfg)
        detection = Detection(
            cfg=cfg, 
            hardware=hardware,
            db=database, 
            camera=camera, 
            recognition=recognition, 
            mqtt_notif=mqtt_notif, 
            mqtt_set=mqtt_set
        )

        hardware.ledControl.setColor(False, False, False)
        hardware.buzzerControl.play(1, 0.05, 0.05)

        # Start threads
        mqtt_notif.start()
        mqtt_set.start()
        camera.start()
        detection.start()

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            detection.isRunning = False
            camera.isRunning = False

        hardware.ledControl.setColor(True, False, False)
        hardware.buzzerControl.play(5, 0.05, 0.05)
        hardware.ledControl.setColor(False, False, False)
