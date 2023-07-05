from src.cloud.kinesis_video_stream_consumer import KinesisVideoStreamConsumer
import time, os, threading

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
        while not Application.stop_mainprocess:
            # Main process here
            time.sleep(1)
