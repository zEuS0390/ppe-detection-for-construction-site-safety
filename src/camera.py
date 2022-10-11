from yolor.utils.datasets import letterbox
from threading import Thread
import cv2
import numpy as np

# Camera Class
class Camera:

    # Initialize
    def __init__(self):
        self.frame = None
        self.cap = cv2.VideoCapture(0)
        self.camThread = Thread(target=self.update)
        self.camThread.start()

    # Update function for the camera thread
    def update(self):
        while self.cap.isOpened():
            _, self.frame = self.cap.read()
            cv2.imshow("frame", self.frame)
            key = cv2.waitKey(30)
            if key & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    # Get the frame with additional dimension to be detected by the model
    def getFrame(self):
        img: np.ndarray = self.frame.copy()
        img = letterbox(img, new_shape=(640, 640), auto=True)[0]
        img = np.expand_dims(img, axis=0)
        img = img.transpose(0, 3, 1, 2)
        return img