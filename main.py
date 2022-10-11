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

def func(cam, det):
    with torch.no_grad():
        while True:
            processed = cam.getFrame()
            if processed is not None:
                det.detect(processed, cam.frame)
            print("Waiting 10 seconds..")

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    confparser = configparser.ConfigParser()
    confparser.read("./config.cfg")
    det = Detection(confparser)
    cam = Camera()
    detThread = threading.Thread(target=func, args=(cam, det))
    detThread.start()
    
