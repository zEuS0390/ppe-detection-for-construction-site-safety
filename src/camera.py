from yolor.utils.datasets import letterbox
from threading import Thread
import numpy as np
import cv2

# Camera Class
class Camera:

    # Initialize
    def __init__(self):
        self.frame = None
        self.cap = cv2.VideoCapture(0)
        self.camThread = Thread(target=self.update)
        self.camThread.start()
        self.det = []

    # Update function for the camera thread
    def update(self):
        while self.cap.isOpened():
            _, self.frame = self.cap.read()
            cv2.imshow("frame", self.frame)
            key = cv2.waitKey(30)
            if key & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    # Get frame with an additional dimension to be used by the detection model
    def getFrame(self):
        if self.frame is not None:
            img: np.ndarray = self.frame.copy()
            img = letterbox(img, new_shape=(640, 640), auto=True)[0]
            img = np.expand_dims(img, axis=0)
            img = img.transpose(0, 3, 1, 2)
            return img