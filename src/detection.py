from configparser import ConfigParser
from yolor.models.models import Darknet
from yolor.utils.datasets import LoadWebcam, letterbox
from yolor.utils.general import non_max_suppression, scale_coords
from yolor.utils.torch_utils import select_device
import torch, random, cv2
import numpy as np

class Detection:

    # Initialize
    def __init__(self, cfg: ConfigParser):
        self.cfg = cfg
        self.names: list = []
        self.colors: list = []
        self.model = None
        self.device = select_device(self.cfg.get("yolor", "device"))

        self.load_classes()
        self.load_model()

    # Load classes
    def load_classes(self):
        with open(self.cfg.get("yolor", "classes")) as f:
            self.names = f.read().split('\n')
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]

    # Load model
    def load_model(self):
        self.model = Darknet(self.cfg.get("yolor", "cfg"), self.cfg.getint("yolor", "img_size")).cpu()
        self.model.load_state_dict(torch.load(self.cfg.get("yolor", "weights"), map_location=self.device)['model'])
        self.model.to(self.device).eval()

    # Detect an image
    def detect(self, frame):
        frame0 = frame
        img = letterbox(frame0, new_shape=(self.cfg.getint("yolor", "img_size"), self.cfg.getint("yolor", "img_size")))[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.float()
        img /= 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        pred = self.model(img, augment=False)[0]
        print("Prediciton done.")
        pred = non_max_suppression(
            pred,
            0.4,
            0.5,
            classes=None,
            agnostic=False
        )
        print("NMS done.")
        gn = torch.tensor(frame0.shape)[[1, 0, 1, 0]]
        for i, det in enumerate(pred):
            s = ''
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame0.shape).round()
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum() 
                s += '%g %ss, ' % (n, self.names[int(c)])
            print(s)

        # cap.release()
