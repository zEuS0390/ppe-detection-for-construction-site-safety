from yolor.utils.datasets import letterbox
from configparser import ConfigParser
from threading import Thread
from datetime import datetime
from src.singleton import Singleton
from queue import Queue
import numpy as np
import cv2, time, logging, os

log = logging.getLogger()

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
    def __init__(
            self, 
            device: str = "0",
            rtsp_enabled: bool = False,
            record_enabled: bool = False
        ):
        self.q = Queue()
        self.frame = None
        self.isRunning = True
        self.q.put(np.zeros((480, 640, 3), dtype=np.uint8))
        log.info("Initializing camera")
        self.device = device
        self.rtsp_enabled = rtsp_enabled
        self.record_enabled = record_enabled
        self.setupVideoCapture()
        if self.record_enabled:
            self.setupRecording()
        log.info("Camera initialized")

    def setupVideoCapture(self):
        while True:
            try:
                if self.device.isdigit():
                    log.info("Choosing in-built camera")
                    self.cap = cv2.VideoCapture(int(self.device))
                else:
                    if self.rtsp_enabled:
                        log.info("Choosing RTSP video stream")
                        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
                        self.cap = cv2.VideoCapture(self.device, cv2.CAP_FFMPEG)
                    else:
                        log.info("Choosing other video stream")
                        self.cap = cv2.VideoCapture(self.device)
                if not self.cap.isOpened():
                    raise Exception("Camera is not detected. Abort.")
                break
            except Exception as e:
                log.error(f"{e}")
            time.sleep(1)

    def setupRecording(self):
        self.fps = 20
        self.frame_size = (640, 480)
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.time_thresh = 1800  # 1800 seconds / 30 minutes
        self.previous_time = time.time()
        self.folder_name = "recording_"+datetime.now().date().strftime("%Y-%m-%d")
        self.dir_path = "data/recordings/{}".format(self.folder_name)
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        self.recording_number = 1
        date_and_time = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")
        self.writer = cv2.VideoWriter(os.path.join(self.dir_path, f"recording_part{self.recording_number}_{date_and_time}.mp4"), self.fourcc, self.fps, self.frame_size)
        self.recording_number += 1

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
            _, read_frame = self.cap.read()

            if self.rtsp_enabled:
                self.q.put(read_frame)
            else:
                self.frame = read_frame

            if self.record_enabled:
                current_time = time.time()
                elapsed_time = current_time - self.previous_time

                if elapsed_time >= self.time_thresh:
                    self.previous_time = current_time
                    self.writer.release()

                    self.folder_name = "recording_"+datetime.now().date().strftime("%Y-%m-%d")
                    self.dir_path = "data/recordings/{}".format(self.folder_name)

                    if not os.path.exists(self.dir_path):
                        os.mkdir(self.dir_path)
                    date_and_time = datetime.now().strftime(r"%y-%m-%d_%H-%M-%S")
                    self.writer = cv2.VideoWriter(os.path.join(self.dir_path, f"recording_part{self.recording_number}_{date_and_time}.mp4"), self.fourcc, self.fps, self.frame_size)
                    self.recording_number += 1

                self.writer.write(read_frame)

            time.sleep(0.03)

        self.cap.release()

        if self.record_enabled:
            self.writer.release()

    def getFrame(self):
        """
        Get frame with an additional dimension to be used by the detection model
        """
        if self.rtsp_enabled:
            original_frame = self.q.get() if self.q.qsize() > 0 else np.zeros((480, 640, 3), dtype=np.unint8)
            img: np.ndarray = original_frame.copy()
        else:
            original_frame = self.frame if self.frame is not None else np.zeros((480, 640, 3), dtype=np.unint8) 
            img: np.ndarray = original_frame.copy()
        img = img[:,:,::-1]
        img = letterbox(img, new_shape=(640, 640), auto=True)[0]
        img = np.expand_dims(img, axis=0)
        img = img.transpose(0, 3, 1, 2)
        return img, original_frame
