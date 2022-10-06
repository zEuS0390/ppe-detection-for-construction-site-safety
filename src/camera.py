import cv2, time, threading

class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.ret = False
        self.running = True

    def run(self):
        while self.cap.isOpened() and self.running:
            self.ret, self.frame = self.cap.read()
            time.sleep(0.3)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

class CameraControllerThread(threading.Thread):

    def __init__(self, cam: Camera, camThread: threading.Thread):
        super(CameraControllerThread, self).__init__()
        self.cam = cam
        self.camThread = camThread

    def run(self):
        self.camThread.start()
        while self.cam.running:
            pass
            time.sleep(0.3)
        self.camThread.join()