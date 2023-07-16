from amazon_kinesis_video_consumer_library.kinesis_video_streams_parser import KvsConsumerLibrary
from amazon_kinesis_video_consumer_library.kinesis_video_fragment_processor import KvsFragementProcessor
from src.db.crud import DatabaseCRUD
import cv2, boto3

class KinesisVideoStreamConsumer:

    def __init__(
            self, 
            aws_kvs_stream_name: str,
            aws_kvs_access_key_id: str, 
            aws_kvs_secret_access_key: str,
            aws_kvs_region: str
    ):
        self.db = DatabaseCRUD.getInstance()
        self.aws_kvs_stream_name = aws_kvs_stream_name
        self.kvs_fragment_processor = KvsFragementProcessor()
        self.last_good_fragment_tags = None
        self.session = boto3.Session(
                region_name=aws_kvs_region,
                aws_access_key_id=aws_kvs_access_key_id,
                aws_secret_access_key=aws_kvs_secret_access_key,
        )
        self.kvs_client = self.session.client("kinesisvideo")
        self.stop_video_stream = False
        self.frames = []
        self.is_active = False
    def _get_data_endpoint(self, stream_name, api_name):
        response = self.kvs_client.get_data_endpoint(
            StreamName=stream_name,
            APIName=api_name
        )
        return response["DataEndpoint"]

    def start_loop(self):
        get_media_endpoint = self._get_data_endpoint(self.aws_kvs_stream_name, "GET_MEDIA")
        kvs_media_client = self.session.client("kinesis-video-media", endpoint_url=get_media_endpoint)
        while not self.stop_video_stream:
            try:
                get_media_response = kvs_media_client.get_media(
                    StreamName=self.aws_kvs_stream_name,
                    StartSelector = {
                        'StartSelectorType': 'NOW'
                    }
                )
                self.my_stream01_consumer = KvsConsumerLibrary(
                    self.aws_kvs_stream_name, 
                    get_media_response, 
                    self.on_fragment_arrived, 
                    self.on_stream_read_complete, 
                    self.on_stream_read_exception
                )
                self.my_stream01_consumer.start()
                self.my_stream01_consumer.join()
                if self.is_active:
                    self.is_active = False
                    self.db.setDeviceDetailsStatus("ZMCI1", False)
            except KeyboardInterrupt as err:
                self.stop_loop()
                raise Exception(f"Keyboard interrupted")
            except Exception as err:
                self.stop_loop()
                raise Exception(f"{err}")
    
    def stop_loop(self):
        if self.is_active:
            self.is_active = False
            self.db.setDeviceDetailsStatus("ZMCI1", False)
        self.my_stream01_consumer.stop_thread()
        self.stop_video_stream = True

    def on_fragment_arrived(self, stream_name, fragment_bytes, fragment_dom, fragment_receive_duration):
        try:
            self.last_good_fragment_tags = self.kvs_fragment_processor.get_fragment_tags(fragment_dom) 
            one_in_frames_ratio = 1
            ndarray_frames = self.kvs_fragment_processor.get_frames_as_ndarray(fragment_bytes, one_in_frames_ratio)
            self.frames += [cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) for frame in ndarray_frames]
            if not self.is_active:
                self.is_active = True
                self.db.setDeviceDetailsStatus("ZMCI1", True)
        except Exception as err:
            print(f"on_fragment_arrived error! {err}")

    def on_stream_read_complete(self, stream_name):
        if self.is_active:
            self.is_active = False
            self.db.setDeviceDetailsStatus("ZMCI1", False)
        print(f'Read Media on stream: {stream_name} Completed successfully - Last Fragment Tags: {self.last_good_fragment_tags}')

    def on_stream_read_exception(self, stream_name, error):
        if self.is_active:
            self.is_active = False
            self.db.setDeviceDetailsStatus("ZMCI1", False)
        print(f'####### ERROR: Exception on read stream: {stream_name}\n####### Fragment Tags:\n{self.last_good_fragment_tags}\nError Message:{error}')

