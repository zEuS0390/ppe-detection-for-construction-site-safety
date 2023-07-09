from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
from src.utils import imageToBinary, binaryToImage
from src.cloud.deployedmodel import DeployedModel
import time, os, threading, json, cv2, logging
import numpy as np

class Application:

    is_detecting = False
    frame_to_be_detected = None

    stop_detectionprocess = False
    stop_mainprocess = False

    @staticmethod
    def main():

        dbHandler = DatabaseCRUD(
            db_URL="mysql+mysqldb://{username}:{password}@{hostname}:{port}/{dbname}".format(
                hostname=os.environ.get("RDS_DB_HOSTNAME"),
                port=int(os.environ.get("RDS_DB_PORT")),
                username=os.environ.get("RDS_DB_USERNAME"),
                password=os.environ.get("RDS_DB_PASSWORD"),
                dbname=os.environ.get("RDS_DB_DBNAME")
            )
        )

        mqttclient = MQTTClient(
            auth_cert=True,
            args = {
                "hostname":os.environ.get("CLOUD_MQTT_HOSTNAME"),
                "port":os.environ.get("CLOUD_MQTT_PORT"),
                "pub_topic":os.environ.get("CLOUD_MQTT_PUB_TOPIC"),
                "sub_topic":os.environ.get("CLOUD_MQTT_SUB_TOPIC"),
                "client_id":os.environ.get("CLOUD_MQTT_CLIENT_ID"),
                "ca_certs":os.environ.get("CLOUD_MQTT_CA_CERTS"),
                "certfile":os.environ.get("CLOUD_MQTT_CERTFILE"),
                "keyfile":os.environ.get("CLOUD_MQTT_KEYFILE")
            }
        )

        deployedmodel = DeployedModel(
            aws_access_key_id=os.environ.get("AWS_SAGEMAKER_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SAGEMAKER_SECRET_ACCESS_KEY"),
            aws_endpoint_name=os.environ.get("AWS_SAGEMAKER_ENDPOINT"),
            aws_region_name=os.environ.get("AWS_SAGEMAKER_REGION")
        )

        kvsconsumer = KinesisVideoStreamConsumer(
            aws_kvs_stream_name=os.environ.get("AWS_KINESIS_VIDEO_STREAM_NAME"),
            aws_kvs_access_key_id=os.environ.get("AWS_KINESIS_VIDEO_STREAM_ACCESS_KEY_ID"),
            aws_kvs_secret_access_key=os.environ.get("AWS_KINESIS_VIDEO_STREAM_SECRET_ACCESS_KEY"),
            aws_kvs_region=os.environ.get("AWS_KINESIS_VIDEO_STREAM_REGION")
        )

        mainProcessThread = threading.Thread(
            target=Application.mainProcessFunc, 
            args = (
                deployedmodel, 
                kvsconsumer
            )
        )

        detectionThread = threading.Thread(
            target=Application.detectFunc,
            args = (
                mqttclient,
                deployedmodel
            )
        )

        mqttclient.start()
        while not mqttclient.is_connected:
            time.sleep(1)

        try:
            detectionThread.start()
            mainProcessThread.start()
            kvsconsumer.start_loop()
        except:
            pass
        mqttclient.stop()
        Application.stop_detectionprocess = True
        Application.stop_mainprocess = True
        kvsconsumer.stop_loop()

    @staticmethod
    def mainProcessFunc(deployedmodel, kvsconsumer):

        cap = cv2.VideoCapture(0)

        frame = np.ndarray((480, 640, 3), dtype=np.uint8)

        while not Application.stop_mainprocess:

            try:
                _, frame = cap.read()
                # frame = kvsconsumer.frames.pop(0)
            except:
                frame = frame

            if not Application.is_detecting:
                Application.frame_to_be_detected = frame
                Application.is_detecting = True
    
            time.sleep(0.01)

        kvsconsumer.stop_loop()

    @staticmethod
    def detectFunc(mqttclient, deployedmodel):
        
        while not Application.stop_detectionprocess:
            if Application.is_detecting == True:
                if Application.frame_to_be_detected is not None:
                    payload = {
                        "image": imageToBinary(Application.frame_to_be_detected),
                        "ppe_preferences": deployedmodel.ppe_preferences
                    }
                    response = deployedmodel.invoke_endpoint(payload)
                    mqttclient.publish(json.dumps(response))
                    cv2.imshow("frame", binaryToImage(response["image"]))
                    Application.is_detecting = False
                    key = cv2.waitKey(25)
                    if key == 27:
                        Application.stop_mainprocess = True
                        Application.stop_detectionprocess = True
                        break
            else:
                time.sleep(0.01)
