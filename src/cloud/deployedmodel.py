from src.singleton import Singleton
import boto3, json

class DeployedModel(metaclass=Singleton):

    def __init__(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            aws_endpoint_name: str,
            aws_region_name: str
    ):

        self.ppe_preferences = {
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

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_endpoint_name = aws_endpoint_name
        self.aws_region_name = aws_region_name
        self.sagemaker_client = boto3.client(
            "sagemaker-runtime",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name
        )
       
    def invoke_endpoint(self, payload):
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.aws_endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload).encode("utf-8")
        )
        result = response["Body"].read().decode()
        return json.loads(result)
