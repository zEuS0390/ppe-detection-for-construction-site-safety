from src.hardware import *
from src.constants import RGBColor
from src.singleton import Singleton

class Indicator(metaclass=Singleton):

    def info_downloading_files(self):
        setColorRGB(*RGBColor.BLUE.value)
        playBuzzer(1, 0.05, 0.05)

    def info_creating_objects(self):
        setColorRGB(*RGBColor.YELLOW.value)
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
        setColorRGB(False, True, True)
        playBuzzer(1, 0.05, 0.05)

    def info_detecting(self):
        setColorRGB(True, False, True)
        playBuzzer(1, 0.1, 0.1)
