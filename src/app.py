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
from datetime import datetime
import logging

logging.basicConfig(filename=f"logs/events_{datetime.now().strftime('%y-%m-%d_%H-%M-%S')}.log",format="%(asctime)s %(message)s", filemode="w")

class Application:

    @staticmethod
    def main():

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Load app configuration file
        logger.info("Loading app configuration")
        cfg = configparser.ConfigParser()
        cfg.read(APP_CFG_FILE)

        # Instantiate objects
        logger.info("Initializing hardware")
        hardware = Hardware(cfg)
        indicator = Indicator()
        shutdownlistener = ShutdownListener()
        logger.info("Hardware initialized")

        logger.info("Downloading model files")
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
        detection.updateThread.join()
        camera.updateThread.join() 

        indicator.info_stopping_application()

        subprocess.run(["sudo", "shutdown", "-h", "now"])

