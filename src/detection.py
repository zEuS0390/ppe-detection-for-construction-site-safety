from configparser import ConfigParser
from yolor.models.models import Darknet
from yolor.utils.torch_utils import select_device
import torch, random

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
        img = torch.zeros((1, 3, self.cfg.getint("yolor", "img_size"), self.cfg.getint("yolor", "img_size")), device=self.device) 
        img = torch.from_numpy(img).to(self.device)
        img = img.float()
        img /= 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        pred = self.model(img, augment=False)[0]
        # Cotinuation
