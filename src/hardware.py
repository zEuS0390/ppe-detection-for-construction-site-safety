from configparser import ConfigParser
from src.singleton import Singleton
try:
    import RPi.GPIO as GPIO
except ImportError:
    # Create a dummy class if GPIO module does not exist
    class GPIO:
        OUT: any = ...
        HIGH: any = ...
        LOW: any = ...
        def setwarnings(*args, **kwargs): ...
        def BCM(*args, **kwargs): ...
        def output(*args, **kwargs): ...
        def setmode(*args, **kwargs): ...
        def setup(*args, **kwargs): ...
        def cleanup(*args, **kwargs): ...
import time

class Hardware(metaclass=Singleton):

    def __init__(self, cfg: ConfigParser):
        self.isrgbenabled = cfg.getboolean("hardware", "rgb_enabled")
        self.isbuzzerenabled = cfg.getboolean("hardware", "buzzer_enabled")
        self.buzzerPin = cfg.getint("hardware", "buzzer_pin")
        self.redPin = cfg.getint("hardware", "red_pin")
        self.greenPin = cfg.getint("hardware", "green_pin")
        self.bluePin = cfg.getint("hardware", "blue_pin")
        self.buttonPin = cfg.getint("hardware", "button_pin")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.setupPins()

    def __del__(self):
        GPIO.cleanup()

    def setupPins(self):
        GPIO.setup(self.buzzerPin, GPIO.OUT)
        GPIO.setup(self.redPin, GPIO.OUT)
        GPIO.setup(self.bluePin, GPIO.OUT)
        GPIO.setup(self.greenPin, GPIO.OUT)
        GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def setColorRGB(red: bool = False, green: bool = False, blue: bool = False):
    hardware = Hardware.getInstance()
    if hardware.isrgbenabled:
        if red == True:
            GPIO.output(hardware.redPin, GPIO.HIGH)
        else:
            GPIO.output(hardware.redPin, GPIO.LOW)
        if green == True:
            GPIO.output(hardware.greenPin, GPIO.HIGH)
        else:
            GPIO.output(hardware.greenPin, GPIO.LOW)
        if blue == True:
            GPIO.output(hardware.bluePin, GPIO.HIGH)
        else:
            GPIO.output(hardware.bluePin, GPIO.LOW)

def playBuzzer(n_times: int, delay1: float, delay2: float):
    hardware = Hardware.getInstance()
    if hardware.isbuzzerenabled:
        for _ in range(n_times):
            GPIO.output(hardware.buzzerPin, GPIO.HIGH)
            time.sleep(delay1)
            GPIO.output(hardware.buzzerPin, GPIO.LOW)
            time.sleep(delay2)
