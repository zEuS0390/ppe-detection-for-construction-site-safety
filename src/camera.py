import cv2, threading

class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.ret = False
        self.running = True

    def run(self):
        while self.cap.isOpened() and self.running:
            self.ret, self.frame = self.cap.read()

    def runSelf(self):
        while self.cap.isOpened() and self.running:
            self.ret, self.frame = self.cap.read()
            if self.ret:
                cv2.imshow("frame", self.frame)
            if cv2.waitKey(30) == 27:
                break
        self.cap.release()
        cv2.destroyAllWindows()

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
        while True:
            if self.cam.frame is not None:
                cv2.imshow("frame", self.cam.frame)
            if cv2.waitKey(30) == 27:
                self.cam.stop()
                break
        self.camThread.join()