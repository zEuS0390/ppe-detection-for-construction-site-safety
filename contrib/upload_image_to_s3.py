import boto3, cv2, os, sys, time
sys.path.append(os.path.abspath("."))
from src.utils import imageToByteStream
from datetime import datetime

class S3Storage:

    def __init__(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        region_name
    ):

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name = region_name
        )

    def upload(self, bucket, key, body, contenttype):
        response = s3storage.s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=contenttype
        )
        return response

    def delete(self, bucket, key):
        response = s3storage.s3_client.delete_object(
            Bucket=bucket,
            Key=key
        )
        return response

if __name__=="__main__":

    # Set up paths
    base_dir = os.path.join("images", "devices")
    device_uuid = "ZMCI1"
    start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    images_group_name = f"{device_uuid}_{start_datetime}"

    # Current directory in this instance
    current_dir = os.path.join(base_dir, device_uuid, images_group_name)

    bucket_name = "pd-ppe-detection-s3-storage"
    s3storage = S3Storage(
        aws_access_key_id=os.environ.get("AWS_S3_STORAGE_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_S3_STORAGE_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_S3_STORAGE_REGION")
    )

    cap = cv2.VideoCapture(0)
    n = 0

    list_of_images = []

    while n < 1:
        ret, frame = cap.read()

        if ret:
            frame_buffer = imageToByteStream(frame)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            current_filename = f"{device_uuid}_{timestamp}.jpg"
            key = os.path.join(current_dir, current_filename).replace("\\", "/")

            start_time = time.time()
            s3storage.upload(
                bucket=bucket_name,
                key=os.path.join("public", key).replace("\\", "/"),
                body=frame_buffer,
                contenttype="image/jpg"
            )
            elapsed_time = time.time() - start_time

            list_of_images.append(key)
            print(f"{key} object was successfully uploaded.")
            time.sleep(0.01)

        n += 1

    input("Press enter to delete all the images. \
          Check the images first in the bucket, before doing this action.")

    while len(list_of_images) > 0:
        key = list_of_images.pop(0)
        s3storage.delete(bucket=bucket_name, key=os.path.join("public", key).replace("\\", "/"))
        print(f"{key} object was successfully deleted.")
        time.sleep(0.01)

    cap.release()
