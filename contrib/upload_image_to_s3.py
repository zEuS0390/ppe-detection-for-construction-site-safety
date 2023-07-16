from io import BytesIO
from PIL import Image
import boto3
import cv2
import os

class S3Storage:

    def __init__(self, bucket_name):

        aws_access_key_id = os.environ.get("AWS_S3_STORAGE_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_S3_STORAGE_SECRET_ACCESS_KEY")
        region_name = os.environ.get("AWS_S3_STORAGE_REGION")

        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name = region_name
        )

if __name__=="__main__":
    s3storage = S3Storage("pd-ppe-detection-s3-storage")
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    if ret:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.from_array(rgb_frame)

        frame_buffer = BytesIO()
        pi_image.save(frame_buffer, format="png")
        frame_buffer.seek(0)

        cv2.waitKey(0)

    cap.release()
