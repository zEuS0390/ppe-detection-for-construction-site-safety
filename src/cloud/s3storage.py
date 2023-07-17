from src.singleton import Singleton
import boto3

class S3Storage(metaclass=Singleton):

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
        response = self.s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType=contenttype
        )
        return response

    def delete(self, bucket, key):
        response = self.s3_client.delete_object(
            Bucket=bucket,
            Key=key
        )
        return response