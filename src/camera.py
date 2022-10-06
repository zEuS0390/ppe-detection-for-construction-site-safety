import cv2

class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def run(self):
        while self.cap.isOpened():
            _, frame = self.cap.read()
            cv2.imshow("frame", frame)
            if cv2.waitKey(30) == 27:
                break
        self.cap.release()
        cv2.destroyAllWindows()