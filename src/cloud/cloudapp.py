from src.utils import imageToBinary, binaryToImage, compressImage, decompressImage, imageToByteStream
from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.cloud.deployedmodel import DeployedModel
from src.cloud.s3storage import S3Storage
from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
import time, os, threading, json, cv2, logging
from datetime import datetime
import numpy as np

class Application:

    # Configuration varaiables
    capture_from_camera_stream = False
    db_save_enabled = False
    detection_enabled = False
    mqtt_enabled = False
    display_image = False

    # Variables for the detection process
    is_detecting = False
    frame_to_be_detected = None

    # Control variables for the two threads
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

        s3storage = S3Storage(
            aws_access_key_id=os.environ.get("AWS_S3_STORAGE_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_S3_STORAGE_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_S3_STORAGE_REGION")
        )

        acquiringFrameThread = threading.Thread(
            target=Application.acquiringFrameFunc, 
            args = (
                kvsconsumer,
            )
        )

        detectionThread = threading.Thread(
            target=Application.detectFunc,
            args = (
                mqttclient,
                deployedmodel
            )
        )

        # Wait and Connect with the MQTT Client
        mqttclient.start()
        while not mqttclient.is_connected:
            time.sleep(1)

        try:
            # Start the processes
            detectionThread.start()
            acquiringFrameThread.start()
            kvsconsumer.start_loop()
        except Exception as err:
            print(f"[Application]: {err}")

        # Wait and stop all processes
        mqttclient.stop()
        Application.stop_mainprocess = True
        Application.stop_detectionprocess = True
        kvsconsumer.stop_loop()

    @staticmethod
    def acquiringFrameFunc(kvsconsumer):

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

            if not Application.is_detecting and kvsconsumer.is_active:
                Application.frame_to_be_detected = frame
                Application.is_detecting = True

            time.sleep(0.01)

        kvsconsumer.stop_loop()

    @staticmethod
    def detectFunc(mqttclient, deployedmodel):

        # Get the instance of the created database handler
        db = DatabaseCRUD.getInstance()

        s3storage: S3Storage = S3Storage.getInstance()

        # Set up paths for using s3 storage
        base_dir = os.path.join("images", "devices")
        device_uuid = "ZMCI1"
        start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        images_group_name = f"{device_uuid}_{start_datetime}"

        # Current directory in this instance
        current_dir = os.path.join(base_dir, device_uuid, images_group_name)

        bucket_name = "pd-ppe-detection-s3-storage"

        # Detection process
        while not Application.stop_detectionprocess:

            if Application.is_detecting:

                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
                current_filename = f"{device_uuid}_{timestamp}.jpg"
                key = os.path.join(current_dir, current_filename).replace("\\", "/")

                message = {
                    "uuid": device_uuid,
                    "image": imageToBinary(Application.frame_to_be_detected),
                    "timestamp": now.strftime("%m/%d/%Y %H:%M:%S"),
                    "total_violations": 0,
                    "total_violators": 0,
                    "total_compliant_ppe": 0,
                    "total_noncompliant_ppe": 0,
                    "violators": []
                }

                # Submit video frame to the deployed detection model
                if Application.detection_enabled:
                    deployedmodel_payload = {
                        "image": imageToBinary(Application.frame_to_be_detected),
                        "ppe_preferences": deployedmodel.ppe_preferences
                    }
                    deployed_model_response = deployedmodel.invoke_endpoint(deployedmodel_payload)
                    message = deployed_model_response

                # Upload the image to s3 storage and save the record in the database
                if Application.db_save_enabled:
                    s3storage.upload(
                        bucket=bucket_name,
                        key=os.path.join("public", key).replace("\\", "/"),
                        body=imageToByteStream(Application.frame_to_be_detected),
                        contenttype="image/jpg"
                    )
                    violationdetails_id = db.insertViolationDetails(key, now)
                    result = db.insertViolationDetailsToDeviceDetails(1, violationdetails_id)
                    for violator in message["violators"]:
                        result = db.insertViolator(
                            violationdetails_id=violationdetails_id,
                            bbox_id=violator["id"],
                            topleft=(0,0),
                            bottomright=(0,0),
                            detectedppe=violator["violations"]
                        )
                        if result:
                            print(f"[DATABASE]: Successfully saved the detection to the database.")
                        else:
                            print(f"[DATABASE]: Failed saving the detection to the database.")

                # Publish through MQTT
                if Application.mqtt_enabled:
                    message["image"] = imageToBinary(
                        decompressImage(
                            compressImage(
                                binaryToImage(message["image"]), 
                                quality=25
                            )
                        )
                    )
                    mqttclient.publish(json.dumps(message))

                # Display the image using OpenCV imshow
                if Application.display_image:
                    # cv2.imshow("frame", Application.frame_to_be_detected)
                    cv2.imshow("frame", binaryToImage(message["image"]))
                    key = cv2.waitKey(25)
                    if key == 27:
                        Application.stop_mainprocess = True
                        Application.stop_detectionprocess = True
                        break

                # Reset back the is_detecting state to False for the next frame
                Application.is_detecting = False

            time.sleep(0.1)

