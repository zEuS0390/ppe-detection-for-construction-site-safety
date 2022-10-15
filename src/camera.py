from yolor.utils.datasets import letterbox
from threading import Thread
import cv2, time
import numpy as np

from yolor.utils.plots import plot_one_box

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
            for det in self.detected:
                label = '%s %.2f' % (det[2], det[1])
                plot_one_box(det[0], self.frame, (0, 255, 0), label=label, line_thickness=3)
            time.sleep(0.03)
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