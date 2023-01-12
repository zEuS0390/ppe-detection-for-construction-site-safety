from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
from src.detection import Detection
from src.utils import getLatestFiles, getRecognitionData
from src.recognition import Recognition
from src.camera import Camera
from src.hardware import Hardware
from src.indicator import Indicator
from src.shutdown_listener import ShutdownListener
from src.constants import APP_CFG_FILE
import configparser, time, subprocess

class Application:

    @staticmethod
    def main():

        # Load app configuration file
        cfg = configparser.ConfigParser()
        cfg.read(APP_CFG_FILE)

        # Instantiate objects
        hardware = Hardware(cfg)
        indicator = Indicator()
        shutdownlistener = ShutdownListener()

        indicator.info_downloading_files()
        getLatestFiles("data", ["face_recognition", "detection"])

        indicator.info_creating_objects()
        dbHandler = DatabaseCRUD(cfg)
        dbHandler.insertPersons(getRecognitionData(cfg)["info"])
        dbHandler.insertPPEClasses(cfg.get("yolor","classes"))

        camera = Camera(cfg)
        recognition = Recognition(cfg)
        mqtt_notif = MQTTClient("notif")
        mqtt_set = MQTTClient("set")
        
        detection = Detection(
            cfg, mqtt_notif, mqtt_set
        )

        # Start threads
        mqtt_notif.start()
        mqtt_set.start()
        camera.start()
        detection.start()

        indicator.info_none()

        shutdownlistener.thread.join()
        detection.isRunning = False
        camera.isRunning = False
        
        indicator.info_stopping_application()

        subprocess.run(["sudo", "shutdown", "-h", "now"])

