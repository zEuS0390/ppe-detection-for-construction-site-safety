from yolor.utils.datasets import letterbox
from src.utils import imageToBinary
from threading import Thread
import numpy as np
import cv2, time, json

# Camera Class
class Camera:

    # Initialize
    def __init__(self, mqtt_client=None):
        self.frame = None
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Camera is not detected. Abort.")
        self.mqtt_client = mqtt_client
        self.updateThread = Thread(target=self.update)    
        self.isRunning = True
        self.det = []

    def start(self):
        self.updateThread.start()

    def update(self):
        """
        Update function for the camera thread
        """
        while self.isRunning:
            _, self.frame = self.cap.read()
            if self.mqtt_client is not None:
                img = imageToBinary(self.frame)
                payload = json.dumps({"image": img})
                self.mqtt_client.client.publish("rpi/camera", payload)
            time.sleep(0.03)

    def getFrame(self):
        """
        Get frame with an additional dimension to be used by the detection model
        """
        if self.frame is not None:
            img: np.ndarray = self.frame.copy()
            img = letterbox(img, new_shape=(640, 640), auto=True)[0]
            img = np.expand_dims(img, axis=0)
            img = img.transpose(0, 3, 1, 2)
            return img
