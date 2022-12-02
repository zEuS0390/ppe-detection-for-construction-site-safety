from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
from src.detection import Detection
from src.utils import getLatestFiles, getRecognitionData
from src.recognition import Recognition
from src.camera import Camera
from src.hardware import Hardware
from src.constants import APP_CFG_FILE, RGBColor
import configparser, time

class Application:

    @staticmethod
    def main():

        # Load app configuration file
        cfg = configparser.ConfigParser()
        cfg.read(APP_CFG_FILE)

        # Instantiate objects
        hardware = Hardware(cfg)

        hardware.setColorRGB(*RGBColor.BLUE.value)
        hardware.playBuzzer(1, 0.05, 0.05)

        getLatestFiles("data", ["face_recognition", "detection"])

        hardware.setColorRGB(*RGBColor.YELLOW.value)
        hardware.playBuzzer(1, 0.05, 0.05)

        dbHandler = DatabaseCRUD(cfg)
        dbHandler.insertPersons(getRecognitionData(cfg)["info"])
        dbHandler.insertPPEClasses(cfg.get("yolor","classes"))

        camera = Camera(cfg)
        recognition = Recognition(cfg)
        mqtt_notif = MQTTClient("notif")
        mqtt_set = MQTTClient("set")
        
        detection = Detection(
            cfg, hardware, dbHandler, camera, recognition, mqtt_notif, mqtt_set
        )

        # Start threads
        mqtt_notif.start()
        mqtt_set.start()
        camera.start()
        detection.start()

        hardware.setColorRGB(*RGBColor.NONE.value)
        hardware.playBuzzer(1, 0.05, 0.05)

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            detection.isRunning = False
            camera.isRunning = False
        
        hardware.setColorRGB(*RGBColor.RED.value)
        hardware.playBuzzer(5, 0.05, 0.05)
        hardware.setColorRGB(*RGBColor.NONE.value)

