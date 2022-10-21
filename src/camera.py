from yolor.utils.datasets import letterbox
from threading import Thread
import numpy as np
import cv2, time

# Camera Class
class Camera:

    # Initialize
    def __init__(self):
        self.frame = None
        self.cap = cv2.VideoCapture(0)
        self.camThread = Thread(target=self.update)    
        self.det = []

    def start(self):
        self.camThread.start()

    def join(self):
        self.camThread.join()

    # Update function for the camera thread
    def update(self):
        while self.cap.isOpened():
            _, self.frame = self.cap.read()
            time.sleep(0.03)

    # Get frame with an additional dimension to be used by the detection model
    def getFrame(self):
        if self.frame is not None:
            img: np.ndarray = self.frame.copy()
            img = letterbox(img, new_shape=(640, 640), auto=True)[0]
            img = np.expand_dims(img, axis=0)
            img = img.transpose(0, 3, 1, 2)
            return img