from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.client import MQTTClient
import time, os, threading, json, cv2
import numpy as np

class Application:

    stop_mainprocess = False

    @staticmethod
    def main():

        kvsconsumer = KinesisVideoStreamConsumer(
            aws_kvs_stream_name=os.environ.get("AWS_KINESIS_VIDEO_STREAM_NAME"),
            aws_kvs_access_key_id=os.environ.get("AWS_KINESIS_VIDEO_STREAM_ACCESS_KEY_ID"),
            aws_kvs_secret_access_key=os.environ.get("AWS_KINESIS_VIDEO_STREAM_SECRET_ACCESS_KEY"),
            aws_kvs_region=os.environ.get("AWS_KINESIS_VIDEO_STREAM_REGION")
        )
        mainProcessThread = threading.Thread(target=Application.mainProcessFunc, args=(kvsconsumer,))

        mainProcessThread.start()
        try:
            kvsconsumer.start_loop()
        except:
            Application.stop_mainprocess = True
            kvsconsumer.stop_loop()

    @staticmethod
    def mainProcessFunc(kvsconsumer):
        frame = np.ndarray((480, 640, 3), dtype=np.uint8)
        while not Application.stop_mainprocess:
            # Main process here
            try:
                frame = kvsconsumer.frames.pop(0)
            except:
                frame = frame
            cv2.imshow("frame", frame)
            key = cv2.waitKey(25)
            if key == 27:
                break
        kvsconsumer.stop_loop()
        time.sleep(2)
