from yolor.utils.general import non_max_suppression, scale_coords
from src.utils import getElapsedTime, getIPAddress
from yolor.utils.torch_utils import select_device
from src.db.database import DatabaseHandler
from yolor.models.models import Darknet
from src.recognition import Recognition
import glob, os, torch, threading, time
from configparser import ConfigParser
from src.box import Box, isColliding
import torch.backends.cudnn as cudnn
from src.utils import imageToBinary, parsePlainConfig
from src.db.crud import loadPersons, insertViolator
from src.client import MQTTClient
from src.db.tables import Person
from src.constants import Class
from src.constants import Color
from src.camera import Camera
from datetime import datetime
import numpy as np
import json
import cv2

class Detection:
    
    """
    Methods:
        - start                 () -> None
        - loadPersons           () -> None
        - loadClasses           () -> None
        - loadModel             () -> None
        - loadPreferences       () -> None
        - plotBox               (image: np.ndarray, coordinates: Box, color: Color, label: str) -> None
        - detect                (img, im0s) -> tuple
        - saveViolations        (detected_persons: dict, violations: list) -> None
        - checkOverlaps         (bbox: Box, bboxes: list) -> list
        - checkViolations       (processed_image: np.ndarray, image: np.ndarray) -> dict
        - update                (interval: int=12) -> None
    """

    # Initialize
    def __init__(self, 
        cfg: ConfigParser,
        db: DatabaseHandler=None,
        camera: Camera=None, 
        recognition: Recognition=None, 
        mqtt_client: MQTTClient=None
    ):
        self.cfg = cfg
        self.db = db
        self.camera = camera
        self.recognition = recognition
        self.mqtt_client = mqtt_client
        self.mqtt_client.client.on_message = self.onClientSet
        self.persons_info: Person = []
        self.names: list = []
        self.model = None
        self.isDetecting = True
        self.device = select_device(self.cfg.get("yolor", "device"))
        cudnn.benchmark = True
        if self.db is not None:
            self.loadPersons()
        self.loadPreferences()
        self.loadColors()
        self.loadClasses()
        self.loadModel()
        self.isRunning = True
        self.camera_details = {
            "name": self.cfg.get("camera", "name"),
            "description": self.cfg.get("camera", "description"),
            "ip_address": getIPAddress()
        }
        self.updateThread = threading.Thread(target=self.update)
        
    def start(self):
        """
        Starts the detection thread. It will not start if one or more required arguments are missing.
        """
        if self.camera is not None and self.recognition is not None and self.mqtt_client is not None: 
            self.updateThread.start()
        else:
            print("Missing arguments (camera, recognition, mqtt_client). Abort")

    def onClientSet(self, client, userdata, msg):
        payload = msg.payload.decode()
        data = json.loads(payload)
        if "ppe_preferences" in data:
            self.ppe_preferences = {class_name.replace("_", " "): status for class_name, status in data["ppe_preferences"].items()}
            print(self.ppe_preferences)

    def loadPersons(self):
        """
        Loads all persons inserted in the database
        """
        self.persons_info = loadPersons(self.db)
        string = ""
        for person in self.persons_info:
            string += f"{person} {self.persons_info[person]['first_name']} loaded.\n"
        print(string, end="")

    def loadColors(self):
        """
        Loads predefined colors for each class names
        """
        string = ""
        self.colors = list(Color)
        for color in [(color.name, color.value) for color in self.colors]:
            string += f"{color[0]} {color[1]} loaded.\n"

    def loadClasses(self):
        """
        Loads class names which were used in the trained model.
        """
        with open(self.cfg.get("yolor", "classes")) as f:
            self.names = f.read().split('\n')

    # Load model
    def loadModel(self):
        """
        Loads the detection model.
        """
        weights = glob.glob(os.path.join(self.cfg.get("yolor", "weights"), "*.pt"))
        if len(weights) == 0:
            raise Exception("No weights found.")
        elif len(weights) > 1:
            raise Exception("Too many weights found.")
        else:
            self.model = Darknet(self.cfg.get("yolor", "cfg"), self.cfg.getint("yolor", "img_size")).cpu()
            self.model.load_state_dict(torch.load(weights[0], map_location=self.device)['model'])
            self.model.to(self.device).eval()

    def loadPreferences(self):
        preferences_cfg = parsePlainConfig(f"cfg/detection/filter.cfg")
        self.ppe_preferences = {class_name.replace("_", " "): True if status == 'on' else False for class_name, status in preferences_cfg.items()}
        print(self.ppe_preferences)
    
    def plotBox(self, image: np.ndarray, coordinates: Box, color: Color, label: str):
        """
        Plot bounding boxes and labels in the image.
        """
        tl = round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1 # Line/font thickness
        cv2.rectangle(
            image, 
            (coordinates.left, coordinates.top), 
            (coordinates.right, coordinates.bottom), 
            color.value, 
            thickness=tl, 
            lineType=cv2.LINE_AA
        )
        font_thickness = max(tl - 1, 1)  # font thickness
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

    def saveViolations(self, persons, violations):
        """
        Save violations of person/s to the database
        """
        violations = [violation["class_name"] for violation in violations]
        for person in persons:
            if len(person) > 0:
                insertViolator(
                    self.db,
                    person_id=person["person_id"],
                    coordinates="(0,0,0,0)",
                    detectedppeclasses=violations,
                    verbose=True
                )

    def checkOverlaps(self, bbox: Box, bboxes: list):
        overlaps = []
        for other_bbox in bboxes:
            if isColliding(bbox, other_bbox["coordinate"]):
                overlaps.append(other_bbox["id"])
        return overlaps

    def checkViolations(self, processed_image, image):
        """
        Analyzes which PPE objects belong to a certain person and recognize identities by checking the overlapping bounding boxes.
        
        Note: It ignores all PPE objects that do not reside within the bounding box of the person class.

        Args:
            processed_image: A processed image with an additional dimension that will be used in the model.
            image: Original image that will be used for plotting bounding boxes of the detected objects.

        Returns the violations of the detected person
        """
        string = ""
        message = {}
        detection_result, detection_time = getElapsedTime(self.detect, processed_image, image)
        string += f"Detection time: {detection_time:.2f}\n"

        image_plots = image.copy()
        persons = detection_result[0]
        ppe = detection_result[1]

        # Plot boxes of the detected objects
        for obj in persons+ppe:
            confidence = obj['confidence']
            class_name = obj["class_name"]
            label = f"{class_name} {confidence:.2f}"
            self.plotBox(image_plots, obj["coordinate"], self.colors[self.names.index(class_name)], label)

        # Check overlaps of each detected ppe item
        for ppe_item in ppe:
            overlaps = self.checkOverlaps(ppe_item["coordinate"], persons)
            ppe_item["overlaps"] = overlaps
        
        # Recognize faces
        person_indices, person_time = getElapsedTime(self.recognition.predict, image, distance_threshold=0.4)
        string += f"Recognition time: {person_time:.2f}\n"

        # Check overlaps of each recognized faces
        recognized_persons = []
        for person_index, person_coordinate in person_indices:
            person_info = self.persons_info[int(person_index)] if person_index != -1 else {}
            box = Box(*person_coordinate)
            self.plotBox(image_plots, box, self.colors[11], person_info["first_name"] if len(person_info) > 0 else "Unknown")
            overlaps = self.checkOverlaps(box, persons)
            person_info["overlaps"] = overlaps
            recognized_persons.append(person_info)

        # Resize image to be published from mqtt client
        image_plots = cv2.resize(image_plots, (240, 240), interpolation=cv2.INTER_AREA)

        # Evaluate violations of each person
        violators = []
        for person in persons:
            violator = {
                "persons": [],
                "violations": []
            } 
            id = person["id"]

            # Get PPE items that are in the person
            for ppe_item in ppe:
                confidence = round(ppe_item["confidence"], 4)
                class_name = ppe_item["class_name"]
                if id in ppe_item["overlaps"]:
                    ppe_item["confidence"] = confidence
                    ppe_item["class_name"] = class_name
                    try:
                        del ppe_item["coordinate"]
                    except Exception as e:
                        pass
                    violator["violations"].append(ppe_item)

            # Get recognized faces that are in the person
            for recognized_person in recognized_persons:
                if id in recognized_person["overlaps"]:
                    violator["persons"].append(recognized_person)

            violators.append(violator)

            # Save violations of person/s to the database
            # if self.db is not None:
            #     _, save_time = getElapsedTime(self.saveViolations, violator["persons"], violator["violations"])
            #     string += f"Saving violations time: {save_time:.2f}\n"

        message["camera"] = self.camera_details
        message["image"] = imageToBinary(image_plots)
        message["violators"] = violators
        message["timestamp"] = datetime.now().strftime(r"%m/%d/%y %H:%M:%S")
        
        print(string, end="")
        return message

    @torch.no_grad()
    def update(self, interval=12):
        """
        Function for update thread
        """
        previous_time = time.time()
        while self.isRunning:
            elapsed_time = time.time() - previous_time
            if elapsed_time >= interval:
                previous_time = time.time()
                try:
                    processed_frame, original_frame = self.camera.getFrame()
                except:
                    print("Returned None on getFrame method")
                    time.sleep(0.03)
                    continue
                if processed_frame is not None:
                    violations_result, violations_time = getElapsedTime(self.checkViolations, processed_frame, original_frame)
                    print(f"Overall process time: {violations_time:.2f}")
                    to_print = {
                        "camera": violations_result["camera"],
                        "violators": violations_result["violators"],
                        "timestamp": violations_result["timestamp"]
                    }
                    print(json.dumps(to_print, indent=4, sort_keys=True))
                    payload = json.dumps(violations_result)
                    self.mqtt_client.publish(payload=payload)
            time.sleep(0.03)
