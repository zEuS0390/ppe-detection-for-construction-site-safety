from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
from src.utils import imageToBinary, binaryToImage, compressImage, decompressImage
from src.cloud.deployedmodel import DeployedModel
import time, os, threading, json, cv2, logging
import numpy as np

class Application:

    capture_from_camera_stream = False
    detection_enabled = False
    mqtt_enabled = False
    display_image = False

    is_detecting = False
    frame_to_be_detected = None

    stop_detectionprocess = False
    stop_mainprocess = False

    @staticmethod
    def main():

        db = DatabaseCRUD(
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

        return

        # Wait and Connect with the MQTT Client
        mqttclient.start()
        while not mqttclient.is_connected:
            time.sleep(1)

        try:
            # Start the processes
            detectionThread.start()
            mainProcessThread.start()
            kvsconsumer.start_loop()
        except Exception as err:
            print(f"[Application]: {err}")

        # Wait and stop all processes
        mqttclient.stop()
        Application.stop_mainprocess = True
        Application.stop_detectionprocess = True
        kvsconsumer.stop_loop()

    @staticmethod
    def mainProcessFunc(deployedmodel, kvsconsumer):

        if Application.capture_from_camera_stream:
            cap = cv2.VideoCapture(0)

        frame = np.ndarray((480, 640, 3), dtype=np.uint8)

        while not Application.stop_mainprocess:

            try:
                if Application.capture_from_camera_stream:
                    frame = cap.read()[1]
                else:
                    frame = kvsconsumer.frames.pop(0)
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

            if Application.is_detecting == True and Application.frame_to_be_detected is not None:

                # Format of mqtt payload with sample data
                mqtt_payload = {
                    "image": imageToBinary(Application.frame_to_be_detected),
                    "timestamp": "11/21/22 12:19:53",
                    "total_violations": 3,
                    "total_violators": 1,
                    "violators": [
                        {
                            "id": 2,
                            "person_info": [
                                {
                                    "first_name": "Nick Frederick",
                                    "job_title": "Contractor",
                                    "last_name": "Smith",
                                    "middle_name": "Bell",
                                    "overlaps": [
                                        2
                                    ],
                                    "person_id": 1
                                }
                            ],
                            "violations": [
                                {
                                    "class_name": "no helmet",
                                    "confidence": 0.852,
                                    "id": 1,
                                    "overlaps": [
                                        2
                                    ]
                                },
                                {
                                    "class_name": "glasses",
                                    "confidence": 0.6996,
                                    "id": 3,
                                    "overlaps": [
                                        2
                                    ]
                                },
                                {
                                    "class_name": "no vest",
                                    "confidence": 0.5462,
                                    "id": 4,
                                    "overlaps": [
                                        2
                                    ]
                                }
                            ]
                        }
                    ]
                }

                if Application.detection_enabled:
                    deployedmodel_payload = {
                        "image": imageToBinary(Application.frame_to_be_detected),
                        "ppe_preferences": deployedmodel.ppe_preferences
                    }
                    deployed_model_response = deployedmodel.invoke_endpoint(deployedmodel_payload)
                    mqtt_payload = deployed_model_response

                if Application.mqtt_enabled:
                    mqtt_payload["image"] = imageToBinary(
                        decompressImage(
                            compressImage(
                                binaryToImage(mqtt_payload["image"]), 
                                quality=12
                            )
                        )
                    )
                    mqttclient.publish(json.dumps(mqtt_payload))

                if Application.display_image:
                    # cv2.imshow("frame", Application.frame_to_be_detected)
                    cv2.imshow("frame", binaryToImage(mqtt_payload["image"]))
                    key = cv2.waitKey(25)
                    if key == 27:
                        Application.stop_mainprocess = True
                        Application.stop_detectionprocess = True
                        break

                Application.is_detecting = False

            else:
                time.sleep(0.01)
