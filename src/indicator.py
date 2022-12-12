from src.hardware import Hardware
from src.constants import RGBColor

class Indicator(Hardware):

    def __init__(self, cfg):
        super(Indicator, self).__init__(cfg)

    def info_downloading_files(self):
        self.setColorRGB(*RGBColor.BLUE.value)
        self.playBuzzer(1, 0.05, 0.05)

    def info_creating_objects(self):
        self.setColorRGB(*RGBColor.YELLOW.value)
        self.playBuzzer(1, 0.05, 0.05)

    def info_none(self, buzzer=True):
        self.setColorRGB(*RGBColor.NONE.value)
        if buzzer:
            self.playBuzzer(1, 0.05, 0.05)

    def info_stopping_application(self):
        self.setColorRGB(*RGBColor.RED.value)
        self.playBuzzer(5, 0.05, 0.05)
        self.setColorRGB(*RGBColor.NONE.value)

    def info_receiving_msg_mqtt(self):
        self.setColorRGB(False, True, True)
        self.playBuzzer(1, 0.05, 0.05)

    def info_detecting(self):
        self.setColorRGB(True, False, True)
        self.playBuzzer(1, 0.1, 0.1)