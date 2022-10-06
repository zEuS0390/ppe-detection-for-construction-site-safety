from src import *
import argparse

"""
    TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES - QUEZON CITY
    PERSONAL PROTECTIVE EQUIPMENT DETECTION USING YOLOR ALGORITHM [2022]
    TEAM MEMBERS:
        - BALTAZAR, ZEUS JAMES
        - BASBACIO, MARTIN LORENZO
		- LARROSA, CLARENCE GAIL
        - MARQUEZ, IAN GABRIEL
"""

def shell(cam: Camera):
    while True:
        try:
            inputmsg = input(">> ")
            if inputmsg == "exit":
                cam.stop()
                break
        except:
            cam.stop()
            break

if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    cam = Camera()
    camThread = threading.Thread(target=cam.run)
    camController = CameraControllerThread(cam, camThread)
    shellThread = threading.Thread(target=shell, args=(cam,))
    shellThread.start()
    camController.start()