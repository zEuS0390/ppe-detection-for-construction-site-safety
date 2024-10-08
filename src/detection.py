from yolor.utils.general import non_max_suppression, scale_coords
from src.utils import getElapsedTime, getIPAddress
from yolor.utils.torch_utils import select_device
from yolor.models.models import Darknet
from configparser import ConfigParser
from src.box import Box, isColliding
import torch.backends.cudnn as cudnn
from src.utils import (
    imageToBinary,
    parsePlainConfig,
    getDetectionModel
)
from src.db.crud import DatabaseCRUD
from src.singleton import Singleton
from src.client import MQTTClient
from src.indicator import Indicator
from src.db.tables import ViolationDetails
import torch, threading, time
from src.constants import (
    Class,
    BGRColor,
    DEFAULT_MQTT_IMG_SIZE
)
from src.camera import Camera
from datetime import datetime
import numpy as np
import json, logging, cv2

class Detection(metaclass=Singleton):

    """
    Methods:
        - start                 () -> None
        - onClientSet           (client, userdata, msg) -> None
        - loadData              () -> None
        - loadCameraDetails     () -> None
        - loadClasses           () -> None
        - loadModel             () -> None
        - loadDetectionCFG      () -> None
        - plotBox               (image: np.ndarray, coordinates: Box, color: Color, label: str) -> None
        - detect                (img, im0s) -> tuple
        - saveViolations        (detected_persons: dict, violations: list) -> None
        - checkOverlaps         (bbox: Box, bboxes: list) -> list
        - checkViolations       (processed_image: np.ndarray, image: np.ndarray) -> dict
        - update                () -> None
    """

    names = []
    model = None
    isDetecting = True
    isRunning = True
    interval = 12
    mqtt_img_size = DEFAULT_MQTT_IMG_SIZE
    camera_details = {}

    # Initialize
    def __init__(self,
        cfg: ConfigParser,
        mqtt_client: MQTTClient = None
    ):
        self.logger = logging.getLogger()
        self.cfg = cfg
        self.mqtt_client = mqtt_client
        self.device = select_device(self.cfg.get("yolor", "device"))
        cudnn.benchmark = True
        self.loadData()
        self.logger.info("Detection initialized")

    def start(self):
        """
        Starts the detection thread. It will not start if one or more required arguments are missing.
        """
        if self.mqtt_client is not None:
            self.indicator: Indicator = Indicator.getInstance()
            self.db: DatabaseCRUD = DatabaseCRUD.getInstance()
            self.devicedetails_id = self.db.insertDeviceDetails(
                kvs_name="",
                bucket_name="pd-ppe-detection-s3-storage",
                uuid="ZMCI1",
                password="pass123",
                pub_topic="ZMCI/test/notif",
                set_topic="ZMCI/test/set",
            )
            self.camera: Camera = Camera.getInstance()
            self.mqtt_client.client.on_message = self.onClientSet
            self.loadCameraDetails()
            self.updateThread = threading.Thread(target=self.update)
            self.updateThread.start()
        else:
            self.logger.error("Missing arguments (camera, mqtt_client). Abortting.")

    def stop(self):
        self.isRunning = False

    def onClientSet(self, client, userdata, msg):
        self.indicator.info_receiving_msg_mqtt()
        self.indicator.info_none(buzzer=False)
        payload = msg.payload.decode()
        try:
            data = json.loads(payload)
            if "ppe_preferences" in data:
                self.ppe_preferences = {class_name.replace("_", " "): status for class_name, status in data["ppe_preferences"].items()}
            if "detection_interval" in data:
                self.interval = data["detection_interval"]
            if "mqtt_img_resolution" in data:
                self.mqtt_img_size[0] = data["mqtt_img_resolution"]["width"]
                self.mqtt_img_size[1] = data["mqtt_img_resolution"]["height"]
        except Exception as e:
            self.logger.error(f"MQTT Client Error: {e}")

    def loadData(self):
        self.loadDetectionCFG()
        self.loadColors()
        self.loadClasses()
        self.loadModel()

    def loadCameraDetails(self):
        self.camera_details["name"] = self.cfg.get("camera", "name"),
        self.camera_details["description"] = self.cfg.get("camera", "description"),
        self.camera_details["ip_address"] = getIPAddress()

    def loadColors(self):
        """
        Loads predefined colors for each class names
        """
        self.colors = list(BGRColor)
        self.logger.info(f"{len(self.colors)} colors loaded.")

    def loadClasses(self):
        """
        Loads class names which were used in the trained model.
        """
        with open(self.cfg.get("yolor", "classes")) as f:
            self.names = f.read().split('\n')
        self.logger.info(f"{len(self.names)} ppe class names loaded.")

    # Load model
    def loadModel(self):
        """
        Loads the detection model.
        """
        weights = getDetectionModel(self.cfg)
        if weights is not None:
            self.model = Darknet(self.cfg.get("yolor", "cfg"), self.cfg.getint("yolor", "img_size")).cpu()
            self.model.load_state_dict(torch.load(weights, map_location=self.device)['model'])
            self.model.to(self.device).eval()
            self.logger.info(f"Model loaded: {weights}")
        else:
            self.logger.error("No weights found")
            raise Exception("No weights found")

    def loadDetectionCFG(self):
        detection_cfg = ConfigParser()
        detection_cfg.read("cfg/detection/config.cfg")
        self.ppe_preferences = {key.replace("_", " "): detection_cfg.getboolean("ppe_preferences", key) for key, _ in detection_cfg.items("ppe_preferences")}
        self.publish_if_violators_exist = detection_cfg.getboolean("mqtt", "publish_if_violators_exist")
        self.logger.info("PPE preferences loaded")

    def plotBox(self, _id: int, image: np.ndarray, coordinates: Box, color: BGRColor, label: str):
        """
        Plot bounding boxes and labels in the image.
        """
        tl = round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1 # Line/font thickness
        # Set the font thickness of text labels
        font_thickness = max(tl - 1, 1)  # font thickness
        # This is the label _id, which is basically a PPE class id.
        # Do not include _id in the plot if it's value is -1
        if _id != -1:
            cv2.putText(image, str(_id), (coordinates.left, coordinates.top), 0, tl / 3, color.value, thickness=font_thickness, lineType=cv2.LINE_AA)
        # Draw the bounding box
        cv2.rectangle(
            image,
            (coordinates.left, coordinates.top),
            (coordinates.right, coordinates.bottom),
            color.value,
            thickness=tl,
            lineType=cv2.LINE_AA
        )
        cv2.putText(image, label, (coordinates.left, coordinates.bottom), 0, tl / 3, color.value, thickness=font_thickness, lineType=cv2.LINE_AA)

    # Detect an image
    def detect(self, processed_image, image):
        processed_image = torch.from_numpy(processed_image).to(self.device)
        processed_image = processed_image.float()
        processed_image /= 255.0
        pred = self.model(processed_image, augment=False)[0]
        pred = non_max_suppression(
            pred,
            0.4,
            0.5,
            classes=0,
            agnostic=False
        )
        persons = []
        ppe = []
        id = 1
        for det in pred:
            im0 = image.copy()
            det[:, :4] = scale_coords(processed_image.shape[2:], det[:, :4], im0.shape).round()
            for *xyxy, conf, cls in det:
                class_name = self.names[int(cls)]
                # Filter class names based on PPE preferences
                if class_name in self.ppe_preferences:
                    if self.ppe_preferences[class_name] == False:
                        continue
                detected_obj = {
                        "id": id,
                        "coordinate": Box(
                            top=int(xyxy[1]),
                            right=int(xyxy[2]),
                            bottom=int(xyxy[3]),
                            left=int(xyxy[0])
                        ),
                        "confidence": float(conf),
                        "class_name": class_name
                }
                id+=1
                if Class(int(cls)) == Class.PERSON:
                    persons.append(detected_obj)
                else:
                    ppe.append(detected_obj)
        return persons, ppe

    def saveViolations(self, image, violations, body_coordinate: Box):
        """
        Save violations of person/s to the database
        """
        date_and_time = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")
        image_name = f"data/images/image_{date_and_time}.jpg"
        cv2.imwrite(image_name,image)

        # Create violation details
        violationdetails = ViolationDetails()
        violationdetails.image = image_name
        violationdetails.timestamp = datetime.now()
        self.db.session.add(violationdetails)
        self.db.session.flush()
        violationdetails_id = violationdetails.id
        self.db.session.commit()
        self.db.session.close()

        self.db.insertViolationDetailsToDeviceDetails(self.devicedetails_id, violationdetails_id)

        self.db.insertViolator(
            violationdetails_id=violationdetails_id,
            bbox_id=1,
            topleft=(body_coordinate.left, body_coordinate.top),
            bottomright=(body_coordinate.right, body_coordinate.bottom),
            detectedppe=violations,
            verbose=True,
            commit=False
        )

        self.db.n_operations += 1
        # Perform commit when n_operations value reaches 5
        if self.db.n_operations >= 5:
            self.logger.info("Committing database operations...")
            self.db.n_operations = 0
            self.db.session.commit()
            self.db.session.close()

    def checkOverlaps(self, bbox: Box, bboxes: list):
        overlaps = []
        for other_bbox in bboxes:
            if isColliding(bbox, other_bbox["coordinate"]):
                overlaps.append(other_bbox["id"])
        return overlaps

    def checkViolations(self, processed_image, image):
        """
        Analyzes which PPE objects belong to a certain person by checking the overlapping bounding boxes.

        Note: It ignores all PPE objects that do not reside within the bounding box of the person class.

        Args:
            processed_image: A processed image with an additional dimension that will be used in the model.
            image: Original image that will be used for plotting bounding boxes of the detected objects.

        Returns the violations of the detected person
        """
        total_violations = 0
        class_bbox_drawn = []
        message = {}
        detection_result, detection_time = getElapsedTime(self.detect, processed_image, image)
        self.logger.info(f"Detection time: {detection_time:.2f}")

        image_plots = image.copy()
        persons = detection_result[0]
        ppe = detection_result[1]

        # Check overlaps of each detected ppe item
        for ppe_item in ppe:
            overlaps = self.checkOverlaps(ppe_item["coordinate"], persons)
            ppe_item["overlaps"] = overlaps

        # Resize image to be published from mqtt client
        image_plots = cv2.resize(image_plots, (self.mqtt_img_size[0], self.mqtt_img_size[1]), interpolation=cv2.INTER_AREA)

        # Evaluate violations of each person
        violators = []
        for person in persons:
            id = person["id"]
            violator = {
                "id": id,
                "violations": []
            }

            # Plot the person's id in the image
            self.plotBox(id, image_plots, person["coordinate"], self.colors[self.names.index(person["class_name"])], "")

            # Get PPE items that are in the person
            for ppe_item in ppe:
                confidence = round(ppe_item["confidence"], 4)
                class_name = ppe_item["class_name"]
                if id in ppe_item["overlaps"]:

                    # Draw PPE if not drawn yet
                    if ppe_item["id"] not in class_bbox_drawn:
                        label = f"{class_name}"
                        class_bbox_drawn.append(ppe_item["id"])
                        try:
                            self.plotBox(-1, image_plots, ppe_item["coordinate"], self.colors[self.names.index(ppe_item["class_name"])], label)
                        except:
                            pass

                    # Do not include ppe_items that have multiple overlaps
                    if len(ppe_item["overlaps"]) == 1:
                        total_violations += 1

                    ppe_item["confidence"] = confidence
                    ppe_item["class_name"] = class_name
                    try:
                        del ppe_item["coordinate"]
                    except Exception as e:
                        pass
                    violator["violations"].append(ppe_item)

            violators.append(violator)

            # Save violations of the violator to the database
            if self.db is not None:
                _, save_time = getElapsedTime(self.saveViolations, image_plots, violator["violations"], person["coordinate"])
                self.logger.info(f"Saving violations time: {save_time:.2f}")

        # Consolidate all the information
        message["camera"] = self.camera_details
        message["image"] = imageToBinary(image_plots)
        message["total_violators"] = len(violators)
        message["total_violations"] = total_violations
        message["violators"] = violators
        message["timestamp"] = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")

        return message

    @torch.no_grad()
    def update(self):
        """
        Function for update thread
        """
        previous_time = time.time()
        while self.isRunning:
            elapsed_time = time.time() - previous_time
            if elapsed_time >= self.interval:
                previous_time = time.time()
                try:
                    processed_frame, original_frame = self.camera.getFrame()
                except Exception as e:
                    self.logger.error(f"Returned None on getFrame method: {e}")
                    time.sleep(0.03)
                    continue
                if processed_frame is not None:
                    self.indicator.info_detecting()
                    self.indicator.info_none(buzzer=False)
                    violations_result, violations_time = getElapsedTime(self.checkViolations, processed_frame, original_frame)
                    self.logger.info(f"Overall process time: {violations_time:.2f}")
                    to_print = {
                            "camera": violations_result["camera"],
                            "total_violators": violations_result["total_violators"],
                            "total_violations": violations_result["total_violations"],
                            "violators": violations_result["violators"],
                            "timestamp": violations_result["timestamp"]
                        }
                    if self.publish_if_violators_exist == True:
                        if violations_result["total_violators"] > 0:
                            self.logger.info(json.dumps(to_print, indent=4, sort_keys=True))
                            payload = json.dumps(violations_result)
                            self.mqtt_client.publish(payload=payload)
                    else:
                        self.logger.info(json.dumps(to_print, indent=4, sort_keys=True))
                        payload = json.dumps(violations_result)
                        self.mqtt_client.publish(payload=payload)
            time.sleep(0.03)
