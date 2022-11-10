from yolor.utils.general import non_max_suppression, scale_coords
from src.utils import getElapsedTime
from yolor.utils.torch_utils import select_device
import torch, random, threading, time
from yolor.models.models import Darknet
from src.recognition import Recognition
from configparser import ConfigParser
import torch.backends.cudnn as cudnn
from src.client import MQTTClient
from src.camera import Camera
from datetime import datetime
from src.box import Box, isColliding
import glob, os

PERSON = 10

class Detection:

    # Initialize
    def __init__(self, cfg: ConfigParser, camera: Camera=None, recognition: Recognition=None, mqtt_client: MQTTClient=None):
        self.cfg = cfg
        self.camera = camera
        self.recognition = recognition
        self.mqtt_client = mqtt_client
        self.names: list = []
        self.colors: list = []
        self.model = None
        self.isDetecting = True
        self.device = select_device(self.cfg.get("yolor", "device"))
        cudnn.benchmark = True
        self.load_classes()
        self.load_model()
        self.isRunning = True
        self.updateThread = threading.Thread(target=self.update)
    
    # Start detection thread
    def start(self):
        if self.camera is not None and self.recognition is not None and self.mqtt_client is not None: 
            self.updateThread.start()
        else:
            print("Missing arguments (camera, recognition, mqtt_client). Abort")

    # Load classes
    def load_classes(self):
        with open(self.cfg.get("yolor", "classes")) as f:
            self.names = f.read().split('\n')
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

    # Load model
    def load_model(self):
        weights = glob.glob(os.path.join(self.cfg.get("yolor", "weights"), "*.pt"))
        if len(weights) == 0:
            raise Exception("No weights found.")
        elif len(weights) > 1:
            raise Exception("Too many weights found.")
        else:
            self.model = Darknet(self.cfg.get("yolor", "cfg"), self.cfg.getint("yolor", "img_size")).cpu()
            self.model.load_state_dict(torch.load(weights[0], map_location=self.device)['model'])
            self.model.to(self.device).eval()

    # Detect an image
    def detect(self, img, im0s):
        img = torch.from_numpy(img).to(self.device)
        img = img.float()
        img /= 255.0
        pred = self.model(img, augment=False)[0]
        pred = non_max_suppression(
            pred,
            0.4,
            0.5,
            classes=0,
            agnostic=False
        )
        for det in pred:
            im0 = im0s.copy()
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            people = []
            ppe = []
            for *xyxy, conf, cls in det:
                detected_obj = {
                        "coordinate": ((int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))),
                        "confidence": float(conf), 
                        "class_name": self.names[int(cls)]
                }
                if int(cls) == PERSON:
                    people.append(detected_obj)
                else:
                    ppe.append(detected_obj)
        return people, ppe

    def stop(self):
        self.isDetecting = False

    def checkViolations(self, processed_image, image):
        """
        Analyzes which PPE objects belong to a specific person by recognizing the identity of the face or at least the knowing presence of the person.
        
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

        violators = []
        for person in detection_result[0]:
            violator = {}
            person_coordinates = Box(
                top = person["coordinate"][0][1],
                right = person["coordinate"][1][0],
                bottom = person["coordinate"][1][0],
                left = person["coordinate"][0][0]
            )
            faces_result, faces_time = getElapsedTime(self.recognition.predict, image, distance_threshold=0.4)
            string += f"Recognition time: {faces_time:.2f}\n"
            faces = []
            for name, loc in faces_result:
                face_coordinates = Box(
                    top = loc[0],
                    right = loc[1],
                    bottom = loc[2],
                    left = loc[3]
                )
                if isColliding(face_coordinates, person_coordinates):
                    faces.append(name)
            violator["faces"] = faces
            violations = []
            for ppe in detection_result[1]:
                ppe_coordinates = Box(
                    top = ppe["coordinate"][0][1],
                    right = ppe["coordinate"][1][0],
                    bottom = ppe["coordinate"][1][1],
                    left = ppe["coordinate"][0][0]
                )
                if isColliding(ppe_coordinates, person_coordinates):
                    violations.append(
                        ppe["class_name"]
                )
            violator["violations"] = violations
            violators.append(violator)
        message["violators"] = violators
        message["timestamp"] = datetime.now().strftime(r"%m/%d/%y %H:%M:%S")
        print(string, end="")
        return message

    @torch.no_grad()
    def update(self, interval=0):
        """
        Function for update thread
        """
        previous_time = time.time()
        while self.isRunning:
            processed_frame = self.camera.getFrame()
            elapsed_time = time.time() - previous_time
            if elapsed_time >= interval:
                previous_time = time.time()
                if processed_frame is not None:
                    violations_result, violations_time = getElapsedTime(self.checkViolations, processed_frame, self.camera.frame)
                    print(f"Overall process time: {violations_time:.2f}")
                    print(violations_result)
            time.sleep(0.03)
