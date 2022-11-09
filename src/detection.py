from yolor.utils.general import non_max_suppression, scale_coords
from src.utils import imageToBinary, getElapsedTime
from yolor.utils.torch_utils import select_device
import torch, random, threading, time, json
from yolor.utils.plots import plot_one_box
from yolor.models.models import Darknet
from src.recognition import Recognition
from configparser import ConfigParser
import torch.backends.cudnn as cudnn
from src.client import MQTTClient
from src.camera import Camera
from datetime import datetime
import cv2, glob, os

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
        result = {}
        for i, det in enumerate(pred):
            s, im0 = '{}'.format(i), im0s.copy()
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum() 
                s += '%g %ss, ' % (n, self.names[int(c)])
            detected = []
            for *xyxy, conf, cls in det:
                label = '%s %.2f' % (self.names[int(cls)], conf)
                detected.append({
                    "position": ((int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))),
                    "confidence": float(conf), 
                    "class_name": self.names[int(cls)]
                })
                plot_one_box(xyxy, im0, label=label, color=self.colors[int(cls)], line_thickness=3)
            im0 = cv2.resize(im0, (240, 240), interpolation=cv2.INTER_AREA)
            result["image"] = imageToBinary(im0)
            result["detected"] = detected
        return result

    def stop(self):
        self.isDetecting = False

    @torch.no_grad()
    def update(self, interval=10):
        """
        Function for update thread
        """
        message = {}
        string = ""
        detection_time = 0
        faces_time = 0
        previous_time = time.time()
        while self.isRunning:
            processed_frame = self.camera.getFrame()
            elapsed_time = time.time() - previous_time
            if elapsed_time >= interval:
                previous_time = time.time()
                if processed_frame is not None:
                    message.clear()
                    string = ""
                    message, detection_time = getElapsedTime(self.detect, processed_frame, self.camera.frame)
                    string += f"Detection time: {detection_time:.2f}\n"
                    if len(message["detected"]):
                        print([cls["class_name"] for cls in message["detected"]])
                        faces_result, faces_time = getElapsedTime(self.recognition.predict, self.camera.frame, distance_threshold=0.4)
                        string += f"Recognition time: {faces_time:.2f}\n"
                        message["faces"] = faces_result
                        message["timestamp"] = datetime.now().strftime(r"%m/%d/%y %H:%M:%S")
                        # Serialize data from detection result
                        payload = json.dumps(message) 
                        # Publish the serialized data to deliver to destination clients
                        self.mqtt_client.publish(payload)
                    string += f"Overall process time: {detection_time + faces_time:.2f}\n"
                    print(string)
            time.sleep(0.03)
