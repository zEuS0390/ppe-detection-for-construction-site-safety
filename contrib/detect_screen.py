import os, sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from src.detection import Detection
from yolor.utils.datasets import letterbox
from src.utils import getElapsedTime
from pynput import keyboard
from configparser import ConfigParser
import numpy as np
import pyautogui, cv2

"""
Additional Dependencies:
>> sudo apt install scrot
>> pip install pyautogui
>> pip install pynput

Where to put this file?
.
├── cfg
├── data
├── scripts
│   └── detect_screen.py
├── src
└── yolor

Run the file in the root directory (rpi-camera):
>> python scripts/detect_screen.py

Note: When the application is running, press 'F9' to take a screenshot and detect objects.
"""

WIDTH = 640
HEIGHT = 480
CONFIG_FILE = "./cfg/app.cfg"
CAM_INTERVAL = 0.03
DETECT_INTERVAL = 0.03

print("Loading detection model...")
cfg = ConfigParser()
cfg.read(CONFIG_FILE)
det = Detection(cfg)

# Initial image (shows black image)
sct = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

# Stores details of detected objects and they will be displayed in the image
detected = []

is_running = True

def processImage(image: np.ndarray) -> np.ndarray:
    """
    Add an additional dimension to the image and convert it from BGR to RGB format. This function will be used in the detection model.
    """
    img: np.ndarray = image.copy()
    img = img[:,:,::-1]
    img = letterbox(img, new_shape=(640, 640), auto=True)[0]
    img = np.expand_dims(img, axis=0)
    img = img.transpose(0, 3, 1, 2)
    return img

def screenCapture() -> np.ndarray:
    """
    Captures the entire screen and returns an image in BGR format.
    """
    image = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    return image

def on_press(key) -> None:
    """
    Key press event function for key listener.
    """
    pass

def on_release(key) -> None:
    """
    Key release event function for key listener.
    """
    global sct, is_running, detected
    if key == keyboard.Key.f9:
        print("Capturing image...")
        sct = screenCapture()
        processedImage = processImage(sct)
        print("Detecting captured image...")
        result, elapsed_time = getElapsedTime(det.detect, processedImage, sct)
        detected = result[0] + result[1]
        string = ""
        if len(result) > 0:
            labels = [det.names[data["class_id"]] for data in detected]
            string += f"Detection result: {labels}\n"
        string += f"Detection time: {elapsed_time}\n"
        print(string, end="")
    elif key == keyboard.Key.esc:
        is_running = False

def draw() -> None:
    """
    Draws bounding boxes and labels of the detected objects in the image.
    """
    global detected
    if len(detected) > 0:
        for obj in detected:
            coordinate = obj["coordinate"]
            confidence = obj["confidence"]
            class_id = obj["class_id"]
            top = coordinate[0][1]
            right = coordinate[1][0]
            bottom = coordinate[1][1]
            left = coordinate[0][0]
            cv2.rectangle(sct, (left, top), (right, bottom), det.colors[class_id].value, 2)
            cv2.putText(sct, f"{det.names[class_id]} {confidence:.2f}", (left, bottom), cv2.FONT_HERSHEY_SIMPLEX, 1, det.colors[class_id].value, 2)
        detected.clear()

def main() -> None:
    """
    Main entry point of the program
    """
    global is_running
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    # Run the listener in a separate thread
    listener.start()
    try:
        while is_running:
            resized = cv2.resize(sct, (640, 480), interpolation=cv2.INTER_AREA)
            draw()
            cv2.imshow("", resized)
            key = cv2.waitKey(30)
            if key & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                listener.stop()
                break
    except KeyboardInterrupt:
        is_running = False
        listener.stop()
        cv2.destroyAllWindows()

# Entry point of the program
if __name__=="__main__":
    main()
