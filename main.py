from src import *
import argparse, threading

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
    cam = Camera()
    cam.runSelf()
    # camThread = threading.Thread(target=cam.run)
    # camController = CameraControllerThread(cam, camThread)
    # camController.start()