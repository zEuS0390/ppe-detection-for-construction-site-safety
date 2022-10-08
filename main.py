from src import *
import argparse, configparser, threading

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
		- LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    confparser = configparser.ConfigParser()
    confparser.read("./config.cfg")
    det = Detection(confparser)
    with torch.no_grad():
        cam = Camera(img_size=640)
        for _, img, im0s, vid_cap in cam:
            if det.isDetecting:
                frame = det.detect(img, im0s)
                cv2.imshow("frame", frame)
        cv2.destroyAllWindows()