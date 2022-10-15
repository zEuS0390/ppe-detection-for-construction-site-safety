from src import *
import argparse, configparser, threading, time

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
		- LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

@torch.no_grad()
def func(cam, det):
    while True:
        processed = cam.getFrame()
        if processed is not None:
            det = det.detect(processed, cam.frame)
            cam.det = det

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    confparser = configparser.ConfigParser()
    confparser.read("./config.cfg")
    det = Detection(confparser)
    cam = Camera()
    time.sleep(10)
    detThread = threading.Thread(target=func, args=(cam, det))
    detThread.start()
    
