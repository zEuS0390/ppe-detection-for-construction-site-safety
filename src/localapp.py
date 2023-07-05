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

# Set up the log event file and its message format
logging.basicConfig(
    filename=f"data/logs/events_{datetime.now().strftime('%y-%m-%d_%H-%M-%S')}.log",
    format="%(asctime)s %(message)s", 
    filemode="w"
)

class Application:
    
    """
    The workflow of the application happens here. Before starting the detection, all 
    the underlying modules will be initialized first. They are essential, especially 
    in loading the models and the people's basic personal identities. These modules 
    have threads to process their initialized data and perform their specific roles. 
    For example, the hardware module will utilize Raspberry Pi's GPIO pins to control 
    the hardware components in the project based on its configuration.
    
    These are the following modules used:
    - Hardware
    - Indicator
    - ShutdownListener
    - DatabaseCRUD
    - Camera
    - Recognition
    - Detection
    - MQTTClient
    """

    @staticmethod
    def main():
        
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Load app configuration file
        logger.info("Loading app configuration")
        cfg = configparser.ConfigParser()
        cfg.read(APP_CFG_FILE)
        
        app_db_section = "mysql_db"
        dbname = cfg.get(app_db_section, "dbname")
        username = cfg.get(app_db_section, "username")
        password = cfg.get(app_db_section, "password")
        hostname = cfg.get(app_db_section, "hostname")
        port = cfg.get(app_db_section, "port")
        try:
            port = int(port) if port != '' else 3306
        except:
            print("Invalid port parameter. It should be an integer number.")
            return

        if username != '' and password != '' and hostname != '' and dbname != '':
            link = f"mysql+mysqldb://{username}:{password}@{hostname}:{port}/{dbname}"
        else:
            print("Missing database connection parameter(s) [dbname, username, password, hostname]")
            return
        
        # Instantiate objects
        logger.info("Initializing hardware")
        hardware = Hardware(cfg)
        indicator = Indicator()
        shutdownlistener = ShutdownListener()
        logger.info("Hardware initialized")

        logger.info("Downloading model files")
        indicator.info_downloading_files()
        getLatestFiles("data", ["face_recognition", "detection"])
        indicator.info_none(buzzer=False)

        dbHandler = DatabaseCRUD(cfg, db_URL=link)
        dbHandler.insertPersons(getRecognitionData(cfg)["info"])
        dbHandler.insertPPEClasses(cfg.get("yolor","classes"))

        camera = Camera(cfg)
        recognition = Recognition(cfg)
        mqtt_notif = MQTTClient("notif")
        mqtt_set = MQTTClient("set")
        
        detection = Detection(cfg, mqtt_notif, mqtt_set)

        # Start threads
        mqtt_notif.start()
        mqtt_set.start()
        camera.start()
        detection.start()

        shutdownlistener.wait()

        detection.stop()
        camera.stop()
        mqtt_notif.stop()
        mqtt_set.stop()
        detection.updateThread.join()
        camera.updateThread.join() 

        indicator.info_stopping_application()

        # Check if auto shutdown is enabled in the app configuration
        if cfg.getboolean("hardware", "auto_shutdown_enabled"):
            subprocess.run(["sudo", "shutdown", "-h", "now"])
