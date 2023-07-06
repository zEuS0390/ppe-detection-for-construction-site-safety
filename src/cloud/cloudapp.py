from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.client import MQTTClient
from src.utils import imageToBinary, binaryToImage
from src.cloud.deployedmodel import DeployedModel
import time, os, threading, json, cv2
import numpy as np

payload = {
    "image": "",
    "ppe_preferences": {
        "helmet": True,
        "no helmet": True,
        "glasses": True,
        "no glasses": True,
        "vest": True,
        "no vest": True,
        "gloves": True,
        "no gloves": True,
        "boots": True,
        "no boots": True
    }
}

class Application:

    stop_mainprocess = False

    @staticmethod
    def main():

        deployedmodel = DeployedModel(
            aws_access_key_id=os.environ.get("AWS_SAGEMAKER_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SAGEMAKER_SECRET_ACCESS_KEY"),
            aws_endpoint_name=os.environ.get("AWS_SAGEMAKER_ENDPOINT"),
            aws_region_name=os.environ.get("AWS_SAGEMAKER_REGION")
        )

        capture = cv2.VideoCapture(0)

        ret, frame = capture.read()

        if ret:
            payload["image"] = imageToBinary(frame)
            response = deployedmodel.invoke_endpoint(payload)
        else:
            print("Reading frame returns an error")

        cv2.imshow("output.png", binaryToImage(response["image"]))

        cv2.waitKey(0)

        capture.release()
    
        """

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

        """

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
