from src.hardware import *
from src.constants import RGBColor
from src.singleton import Singleton
import time

class Indicator(metaclass=Singleton):

    """
    This class contains all methods indicating a variety of events in the application.

    Methods:
        - info_downloading_files        ()
        - info_none                     ()
        - info_stopping_application     ()
        - info_receving_msg_mqtt        ()
        - info_detecting                ()
    """

    def info_downloading_files(self):
        setColorRGB(*RGBColor.BLUE.value)
        playBuzzer(1, 0.05, 0.05)

    def info_none(self, buzzer=True):
        setColorRGB(*RGBColor.NONE.value)
        if buzzer:
            playBuzzer(1, 0.05, 0.05)

    def info_stopping_application(self):
        setColorRGB(*RGBColor.RED.value)
        playBuzzer(5, 0.05, 0.05)
        setColorRGB(*RGBColor.NONE.value)

    def info_receiving_msg_mqtt(self):
        setColorRGB(*RGBColor.CYAN.value)
        playBuzzer(1, 0.05, 0.05)

    def info_detecting(self):
        setColorRGB(*RGBColor.PURPLE.value)
        playBuzzer(1, 0.1, 0.1)
