from yolor.utils.datasets import letterbox
from configparser import ConfigParser
from threading import Thread
from datetime import datetime
from src.singleton import Singleton
from queue import Queue
import numpy as np
import cv2, time, logging, os

# Camera Class
class Camera(metaclass=Singleton):

    """
    Methods:
        - start     ()
        - stop      ()
        - update    ()
        - getFrame  ()
    """

    # Initialize
    def __init__(self, cfg: ConfigParser):
        self.logger = logging.getLogger()
        self.logger.info("Initializing camera")
        self.frame = None
        self.cfg = cfg
        self.device: str = cfg.get("camera", "device")
        self.rtsp_enabled: bool = self.cfg.getboolean("camera", "rtsp_enabled")
        self.record_enabled: bool = self.cfg.getboolean("camera", "record_enabled")
        while True:
            try:
                if self.device.isdigit():
                    self.logger.info("Choosing in-built camera")
                    self.cap = cv2.VideoCapture(int(self.device))
                else:
                    if self.rtsp_enabled:
                        self.logger.info("Choosing RTSP video stream")
                        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
                        self.cap = cv2.VideoCapture(self.device, cv2.CAP_FFMPEG)
                    else:
                        self.logger.info("Choosing other video stream")
                        self.cap = cv2.VideoCapture(self.device)
                if not self.cap.isOpened():
                    raise Exception("Camera is not detected. Abort.")
                break
            except Exception as e:
                self.logger.error(f"{e}")
            time.sleep(1)
        if self.record_enabled == True:
            self.fps = 20
            self.frame_size = (640, 480)
            self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.time_thresh = 1800  # 1800 seconds
            self.previous_time = time.time()
            self.writer = None
            self.recording_number = 1
        self.isRunning = True
        self.det = []
        self.q = Queue()
        self.q.put(self.cap.read()[1])
        self.logger.info("Camera initialized")

    def start(self):
        self.updateThread = Thread(target=self.update)
        self.updateThread.start()

    def stop(self):
        self.isRunning = False

    def update(self):
        """
        Update function for the camera thread
        """
        while self.isRunning:
            current_time = time.time()
            elapsed_time = current_time - self.previous_time
            _, read_frame = self.cap.read()
            if self.rtsp_enabled:
                self.q.put(read_frame)
            else:
                self.frame = read_frame
            if self.record_enabled:
                if elapsed_time >= self.time_thresh:
                    self.previous_time = current_time
                    if self.writer is not None:
                        self.writer.release()
                    date_and_time = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")
                    self.writer = cv2.VideoWriter(f"data/recordings/recording_part{self.recording_number}_{date_and_time}.mp4", self.fourcc, self.fps, self.frame_size)
                    self.recording_number += 1
                self.writer.write(read_frame)
            time.sleep(0.03)
        self.cap.release()
        self.writer.release()

    def getFrame(self):
        """
        Get frame with an additional dimension to be used by the detection model
        """
        if self.rtsp_enabled:
            if self.q.qsize() > 0:
                original_frame = self.q.get()
                img: np.ndarray = original_frame.copy()
                img = img[:,:,::-1]
                img = letterbox(img, new_shape=(640, 640), auto=True)[0]
                img = np.expand_dims(img, axis=0)
                img = img.transpose(0, 3, 1, 2)
                return img, original_frame
        else:
            if self.frame is not None:
                original_frame = self.frame
                img: np.ndarray = original_frame.copy()
                img = img[:,:,::-1]
                img = letterbox(img, new_shape=(640, 640), auto=True)[0]
                img = np.expand_dims(img, axis=0)
                img = img.transpose(0, 3, 1, 2)
                return img, original_frame
