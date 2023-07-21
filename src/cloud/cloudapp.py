from src.utils import imageToBinary, binaryToImage, compressImage, decompressImage, imageToByteStream
from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
from src.cloud.deployedmodel import DeployedModel
from src.cloud.s3storage import S3Storage
from src.db.crud import DatabaseCRUD
from src.client import MQTTClient
import time, os, threading, json, cv2, logging
from datetime import datetime
# from configparser import ConfigParser
import numpy as np

from sqlalchemy import and_
from src.db.tables import *

class Application:

    # Configuration varaiables
    capture_from_camera_stream = False
    db_save_enabled = True
    detection_enabled = True
    mqtt_enabled = True
    display_image = False

    # Variables for the detection process
    is_detecting = False
    frame_to_be_detected = None

    # Control variables for the two threads
    stop_detectionprocess = False
    stop_mainprocess = False

    @staticmethod
    def main():

        # cfg = ConfigParser()
        # cfg.read("cfg/app.cfg")
        db = DatabaseCRUD(
            db_URL="mysql+mysqldb://{username}:{password}@{hostname}:{port}/{dbname}".format(
                hostname=os.environ.get("RDS_DB_HOSTNAME"),
                port=int(os.environ.get("RDS_DB_PORT")),
                username=os.environ.get("RDS_DB_USERNAME"),
                password=os.environ.get("RDS_DB_PASSWORD"),
                dbname=os.environ.get("RDS_DB_DBNAME")
            )
        )
        # db.insertPPEClasses(cfg.get("yolor", "classes"))

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

        mqttclient.client.on_message = Application.setPreferences

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
                    "total_helmet": 0,
                    "total_glasses": 0,
                    "total_vest": 0,
                    "total_gloves": 0,
                    "total_boots": 0,
                    "total_no_helmet": 0,
                    "total_no_glasses": 0,
                    "total_no_vest": 0,
                    "total_no_gloves": 0,
                    "total_no_boots": 0,
                    "violators": []
                }

                # Submit video frame to the deployed detection model
                if Application.detection_enabled:
                    deployedmodel_payload = {
                        "image": imageToBinary(Application.frame_to_be_detected),
                        "ppe_preferences": deployedmodel.ppe_preferences
                    }
                    deployed_model_response = deployedmodel.invoke_endpoint(deployedmodel_payload)
                    message.update(deployed_model_response)

                # Upload the image to s3 storage and save the record in the database
                if Application.db_save_enabled and len(message["violators"]) > 0:

                    s3storage.upload(
                        bucket=bucket_name,
                        key=os.path.join("public", key).replace("\\", "/"),
                        body=imageToByteStream(binaryToImage(message["image"])),
                        contenttype="image/jpg"
                    )

                    session = db.scoped()
                    session.expire_on_commit = False

                    violationdetails = ViolationDetails()
                    violationdetails.image = key, 
                    violationdetails.timestamp = now,
                    violationdetails.total_violations = int(message["total_violations"]),
                    violationdetails.total_violators = int(message["total_violators"]),
                    violationdetails.total_compliant_ppe = int(message["total_compliant_ppe"]),
                    violationdetails.total_noncompliant_ppe = int(message["total_noncompliant_ppe"]),
                    violationdetails.total_helmet = int(message["total_helmet"]),
                    violationdetails.total_glasses = int(message["total_glasses"]),
                    violationdetails.total_vest = int(message["total_vest"]),
                    violationdetails.total_gloves = int(message["total_gloves"]),
                    violationdetails.total_boots = int(message["total_boots"]),
                    violationdetails.total_no_helmet = int(message["total_no_helmet"]),
                    violationdetails.total_no_glasses = int(message["total_no_glasses"]),
                    violationdetails.total_no_vest = int(message["total_no_vest"]),
                    violationdetails.total_no_gloves = int(message["total_no_gloves"]),
                    violationdetails.total_no_boots = int(message["total_no_boots"])
                    session.add(violationdetails)
                    session.commit()

                    devicedetails = session.query(DeviceDetails).filter(DeviceDetails.uuid == "ZMCI1").scalar()
                    print(devicedetails.uuid)
                    devicedetails.violationdetails.append(violationdetails)
                    session.commit()
    
                    # Iterate to all violators for adding the rows for Violator table
                    for violator in message["violators"]:
                        bbox_id = violator["id"]
                        x1 = violator["x1"]
                        y1 = violator["y1"]
                        x2 = violator["x2"]
                        y2 = violator["y2"]

                        violator = Violator(
                            bbox_id = bbox_id,
                            x1 = x1, y1 = y1,
                            x2 = x2, y2 = y2,
                            violationdetails = violationdetails,
                        )

                        session.add(violator)

                    # Iterate to all violators for adding the rows for DetectedPPEClass table
                    for violator in message["violators"]:
                        detectedppeclasses = violator["violations"]

                        for detectedppeclass in detectedppeclasses:
                            detectedppeclass_bbox_id = detectedppeclass["id"]
                            class_name = detectedppeclass["class_name"]
                            confidence = detectedppeclass["confidence"]
                            overlaps = detectedppeclass["overlaps"]
                            x1 = int(detectedppeclass["x1"])
                            y1 = int(detectedppeclass["y1"])
                            x2 = int(detectedppeclass["x2"])
                            y2 = int(detectedppeclass["y2"])

                            # Check if there is an existing row of PPEClass table
                            ppeclass = session.query(PPEClass).filter_by(class_name=class_name).first()

                            if ppeclass is not None:

                                # Check if there is an existing DetectedPPEClass table
                                detectedppeclass = session.query(DetectedPPEClass).\
                                        join(OverlappingViolator).\
                                        join(Violator).\
                                        filter(
                                            DetectedPPEClass.bbox_id == detectedppeclass_bbox_id,
                                            OverlappingViolator.violator_id == Violator.id,
                                            Violator.violationdetails_id == violationdetails.id
                                        ).scalar()

                                if detectedppeclass is None: 
                                    detectedppeclass = DetectedPPEClass(
                                        bbox_id=detectedppeclass_bbox_id,
                                        ppeclass=ppeclass,
                                        confidence=confidence,
                                        x1 = x1, y1 = y1,
                                        x2 = x2, y2 = y2
                                    )

                                # Iterate to all given bbox overlaps to violators
                                for overlapping_violator_bbox_id in overlaps:

                                    # Get the instance of the violator based on its bbox_id
                                    violator = session.query(Violator).\
                                            join(ViolationDetails).\
                                            filter(and_(
                                                Violator.bbox_id==overlapping_violator_bbox_id,
                                                ViolationDetails.id==violationdetails.id
                                            )).scalar()

                                    # Check if the violator exists
                                    if violator is not None:

                                        # Check if the overlapping violator has been previously added in the detectedppeclass
                                        existing_violator = session.query(Violator).\
                                                join(OverlappingViolator).\
                                                join(DetectedPPEClass).\
                                                filter(and_(
                                                    OverlappingViolator.violator_id == violator.id,
                                                    DetectedPPEClass.id == detectedppeclass.id
                                                )).scalar()

                                        if existing_violator is None:
                                            detectedppeclass.violators.append(violator)

                                session.add(detectedppeclass)
                                session.commit()

                    session.commit()
                    session.close()

                    print(f"[DATABASE]: Successfully saved the detection to the database.")

                # Publish through MQTT
                if Application.mqtt_enabled and len(message["violators"]) > 0:
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

    @staticmethod
    def setPreferences(client, userdata, msg):
        payload = msg.payload.decode()
        try:
            print(payload)
        except Exception as err:
            print(f"[SET PREFERENCES ERROR]: {err}")
