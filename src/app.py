from src.db.database import DatabaseHandler
from src.db.crud import *
from src.db.tables import *
from sqlalchemy import select
from src.client import MQTTClient
from src.detection import Detection
from src.utils import checkLatestWeights, getLatestFile
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

        face_rec_model = getLatestFile(cfg_name="face_recognition", file_extension=".clf")
        if face_rec_model is not None:
            cfg.set("face_recognition", "model", face_rec_model)
            with open("./cfg/app.cfg", "w") as cfg_file:
                cfg.write(cfg_file)

        hardware = Hardware(cfg)
        
        hardware.ledControl.setColor(False, False, True)

        # Check latest weights file
        checkLatestWeights()

        hardware.ledControl.setColor(True, True, False)
        hardware.buzzerControl.play(1, 0.05, 0.05)

        # Instantiate objects
        database = DatabaseHandler(cfg=cfg)
        insertPersons(database, cfg.get("face_recognition", "persons"))
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
