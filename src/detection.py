from configparser import ConfigParser
import torch.backends.cudnn as cudnn
from yolor.models.models import Darknet
from yolor.utils.general import non_max_suppression, scale_coords
from yolor.utils.torch_utils import select_device
from yolor.utils.plots import plot_one_box
import torch, random, threading, time, json
from .utils import imageToBinary
import cv2, glob, os

class Detection:

    # Initialize
    def __init__(self, cfg: ConfigParser):
        self.cfg = cfg
        self.names: list = []
        self.colors: list = []
        self.model = None
        self.isDetecting = True
        self.device = select_device(self.cfg.get("yolor", "device"))
        cudnn.benchmark = True
        self.load_classes()
        self.load_model()
    
    # Start detection thread
    def start(self, cam, func, rec, mqtt_client):
        self.detThread = threading.Thread(target=func, args=(cam, self, rec, mqtt_client))
        self.detThread.start()

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
        start_time = time.time()
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
        elapsed_time = time.time() - start_time
        print(f"Detection time: {elapsed_time:.2f}")
        return result

    def stop(self):
        self.isDetecting = False

# Function for detection thread
@torch.no_grad()
def detThreadFunc(cam, det, rec, mqtt_client):
    external_last_time = time.time()
    while cam.cap.isOpened():
        processed = cam.getFrame()
        external_elapsed_time = time.time() - external_last_time
        # Activate detection every 10 seconds
        if external_elapsed_time > 15:
            external_last_time = time.time()
            if processed is not None:
                internal_last_time = time.time()
                result = det.detect(processed, cam.frame)
                result["faces"] = []
                if len(result["detected"]):
                    faces = rec.predict(cam.frame, distance_threshold=0.4)
                    result["faces"] = faces
                    # Serialize data from detection
                    payload = json.dumps(result) 
                    # Publish the serilized data to deliver to destination clients
                    mqtt_client.client.publish(mqtt_client.topic, payload=payload)
                internal_elapsed_time = time.time() - internal_last_time
                print(f"Overall process time: {internal_elapsed_time:.2f}")
        time.sleep(0.03)
