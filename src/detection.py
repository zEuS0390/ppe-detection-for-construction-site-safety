from configparser import ConfigParser
import torch.backends.cudnn as cudnn
from yolor.models.models import Darknet
from yolor.utils.general import non_max_suppression, scale_coords
from yolor.utils.torch_utils import select_device
from yolor.utils.plots import plot_one_box
import torch, random

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
        boxes = []
        for i, det in enumerate(pred):
            s, im0 = '{}'.format(i), im0s.copy()
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum() 
                s += '%g %ss, ' % (n, self.names[int(c)])
            for *xyxy, conf, cls in det:
                # label = '%s %.2f' % (self.names[int(cls)], conf)
                boxes.append((xyxy, conf, self.names[int(cls)]))
                # plot_one_box(xyxy, im0, label=label, color=self.colors[int(cls)], line_thickness=3)
        return boxes

    def stop(self):
        self.isDetecting = False