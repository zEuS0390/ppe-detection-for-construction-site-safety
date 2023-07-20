from utils.general import non_max_suppression, scale_coords
from utils.torch_utils import select_device
from utils.datasets import letterbox
from models.models import Darknet
from dataclasses import dataclass
import torch.backends.cudnn as cudnn
import torch, os, base64, cv2, json, logging
from datetime import datetime
import numpy as np
from enum import Enum

logging.basicConfig(level=logging.INFO)

class BGRColor(Enum):
    """
    The colors in BGR format. This is used for coloring 
    the bounding boxes of detected objects in the image.
    """
    RED = (0, 0, 255)
    ORANGE = (0, 165, 255)
    YELLOW = (0, 255, 255)
    GREEN = (0, 255, 0)
    SPRING_GREEN = (124, 208, 38)
    CYAN = (255, 255, 0)
    AZURE = (255, 127, 0)
    BLUE = (255, 0, 0)
    VIOLET = (128, 0, 128)
    MAGENTA = (255, 0, 255)
    ROSE = (127, 0, 255)
    BISQUE = (242, 210, 189)

device = select_device("cpu")
names = [
    "helmet",
    "no helmet",
    "glasses",
    "no glasses",
    "vest",
    "no vest",
    "gloves",
    "no gloves",
    "boots",
    "no boots",
    "person"
]
colors = list(BGRColor)
compliant_ppe = [
    "helmet",
    "glasses",
    "vest",
    "gloves",
    "boots"
]
noncompliant_ppe = [
    "no helmet",
    "no glasses",
    "no vest",
    "no gloves",
    "no boots"
]

@dataclass
class Box:
    """
    A class that contains coordinates of the bounding box
    """
    top: int
    right: int
    bottom: int
    left: int

class Class(Enum):
    """
    The class label names arranged in order.
    """
    HELMET = 0
    NO_HELMET = 1
    GLASSES = 2
    NO_GLASSES = 3
    VEST = 4
    NO_VEST = 5
    GLOVES = 6
    NO_GLOVES = 7
    BOOTS = 8
    NO_BOOTS = 9
    PERSON = 10

def isColliding(box_1: Box, box_2: Box):
    """
    Check collision between the bounding box's edges by using AABB (Axis-Aligned Bounding Box) algorithm
    """
    if box_1.left < box_2.right and box_1.right > box_2.left and box_1.bottom > box_2.top and box_1.top < box_2.bottom:
      return True
    return False

def processImage(original_frame):
    img: np.ndarray = original_frame.copy()
    img = img[:,:,::-1]
    img = letterbox(img, new_shape=(640, 640), auto=True)[0]
    img = np.expand_dims(img, axis=0)
    img = img.transpose(0, 3, 1, 2)
    return img

def imageToBase64String(image):
    _, buffer = cv2.imencode(".jpg", image)
    binary_string = base64.b64encode(buffer)
    return binary_string.decode()

def base64StringToImage(encodedByte64Image):
    buffer = base64.b64decode(encodedByte64Image)
    npimg = np.frombuffer(buffer, dtype=np.uint8)
    img = cv2.imdecode(npimg, 1)
    frame = cv2.resize(img, (640, 640), interpolation=cv2.INTER_AREA)
    return frame

def checkOverlaps(bbox: Box, bboxes: list):
    overlaps = []
    for other_bbox in bboxes:
        if isColliding(bbox, other_bbox["coordinate"]):
          overlaps.append(other_bbox["id"])
    return overlaps

@torch.no_grad()
def model_fn(model_dir):
    model_file = os.path.join(model_dir, "best_overall.pt")
    cfg_file = os.path.join(model_dir, "yolor_csp_custom.cfg")
    logging.info("Path of CFG file is in \"" + cfg_file + "\"")
    cudnn.benchmark = True
    model = Darknet(cfg_file, 640).cpu()
    model.load_state_dict(torch.load(model_file, map_location=device)['model'])
    model.to(device).eval()
    logging.info("Successfully loaded the model..")
    return model

def input_fn(request_body, content_type):
    logging.info("Data received...")
    if content_type == 'application/json':
        logging.info("The type of data received is " + str(type(request_body)))
        input_data = json.loads(request_body)
        original_image = base64StringToImage(input_data["image"])
        processed_image = processImage(original_image)
        ppe_preferences = input_data["ppe_preferences"]
        return processed_image, original_image, ppe_preferences
    else:
        logging.info("The data format is not set as \"application/json\"")
        raise ValueError("Invalid data format")

def plotBox(_id: int, image: np.ndarray, coordinates: Box, color: BGRColor, label: str):
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

@torch.no_grad()
def predict_fn(input_data, model):

    total_compliant_ppe = 0
    total_noncompliant_ppe = 0

    logging.info("Running YOLOR detection...")

    processed_image = input_data[0]
    original_image = input_data[1]
    ppe_preferences = input_data[2]
    processed_image = torch.from_numpy(processed_image).to(device)
    processed_image = processed_image.float()
    processed_image /= 255.0
    pred = model(processed_image, augment=False)[0]
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
        im0 = original_image.copy()
        det[:, :4] = scale_coords(processed_image.shape[2:], det[:, :4], im0.shape).round()
        for *xyxy, conf, cls in det:
            class_name = names[int(cls)]
            if class_name in compliant_ppe:
                total_compliant_ppe += 1
            if class_name in noncompliant_ppe:
                total_noncompliant_ppe += 1
            # Filter class names based on PPE preferences
            if class_name in ppe_preferences:
                if ppe_preferences[class_name] == False:
                    continue
            detected_obj = {
              "id": id,
              "coordinate": Box(
                  top=int(xyxy[1]), 
                  right=int(xyxy[2]), 
                  bottom=int(xyxy[3]), 
                  left=int(xyxy[0])
              ),
              "x1": int(xyxy[0]),
              "y1": int(xyxy[1]),
              "x2": int(xyxy[2]),
              "y2": int(xyxy[3]),
              "confidence": float(conf), 
              "class_name": class_name
            }
            id+=1
            if Class(int(cls)) == Class.PERSON:
                persons.append(detected_obj)
            else:
                ppe.append(detected_obj)

    return persons, ppe, original_image, (total_compliant_ppe, total_noncompliant_ppe)

def output_fn(prediction, content_type):

    logging.info("Preparing to send the output...")

    class_bbox_drawn = []
    message = {}

    persons, ppe = prediction[:2]
    original_image = prediction[2].copy()
    image_plots = prediction[2].copy()
    total_compliant_ppe, total_noncompliant_ppe = prediction[3]

    # Check overlaps of each detected ppe item
    for ppe_item in ppe:
        overlaps = checkOverlaps(ppe_item["coordinate"], persons)
        ppe_item["overlaps"] = overlaps

    # Evaluate violations of each person
    violators = []
    for person in persons:

        id = person["id"]
        violator = {
            "id": id, 
            "x1": person["x1"],
            "y1": person["y1"],
            "x2": person["x2"],
            "y2": person["y2"],
            "person_info": [],
            "violations": []
        } 

        # Plot the person's id in the image
        plotBox(id, image_plots, person["coordinate"], colors[names.index(person["class_name"])], "")

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
                        plotBox(-1, image_plots, ppe_item["coordinate"], colors[names.index(ppe_item["class_name"])], label)
                    except:
                        pass

                ppe_item["confidence"] = confidence
                ppe_item["class_name"] = class_name
                try:
                    del ppe_item["coordinate"]
                except Exception as e:
                    pass
                violator["violations"].append(ppe_item)

        violators.append(violator)

    logging.info("Consolidating message...")
    
    message["image"] = imageToBase64String(image_plots)
    message["total_violators"] = len(violators)
    message["total_violations"] = len(ppe) 
    message["total_compliant_ppe"] = total_compliant_ppe
    message["total_noncompliant_ppe"] = total_noncompliant_ppe
    message["violators"] = violators
    message["timestamp"] = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")

    return json.dumps(message)
