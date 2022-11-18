from configparser import ConfigParser
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

class BuzzerControl:

    def __init__(self, buzzerPin: int):
        self.isenabled = False
        self.buzzerPin: int = buzzerPin

    def play(self, n_times: int, delay1: float, delay2: float):
        if self.isenabled:
            for _ in range(n_times):
                GPIO.output(self.buzzerPin, GPIO.HIGH)
                time.sleep(delay1)
                GPIO.output(self.buzzerPin, GPIO.LOW)
                time.sleep(delay2)

class LEDControl:

    def __init__(self, redPin: int, greenPin: int, bluePin: int):
        self.isenabled = False
        self.redPin: int = redPin
        self.greenPin: int = greenPin
        self.bluePin: int = bluePin

    def setColor(self, red: bool = False, green: bool = False, blue: bool = False):
        if self.isenabled:
            if red == True:
                GPIO.output(self.redPin, GPIO.HIGH)
            else:
                GPIO.output(self.redPin, GPIO.LOW)
            if green == True:
                GPIO.output(self.greenPin, GPIO.HIGH)
            else:
                GPIO.output(self.greenPin, GPIO.LOW)
            if blue == True:
                GPIO.output(self.bluePin, GPIO.HIGH)
            else:
                GPIO.output(self.bluePin, GPIO.LOW)

class Hardware:

    def __init__(self, cfg: ConfigParser):
        self.isrgbenabled = cfg.getboolean("hardware", "rgb_enabled")
        self.isbuzzerenabled = cfg.getboolean("hardware", "buzzer_enabled")
        self.buzzerPin = cfg.getint("hardware", "buzzer_pin")
        self.redPin = cfg.getint("hardware", "red_pin")
        self.greenPin = cfg.getint("hardware", "green_pin")
        self.bluePin = cfg.getint("hardware", "blue_pin")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.setupPins()
        self.ledControl = LEDControl(self.redPin, self.bluePin, self.greenPin)
        self.ledControl.isenabled = self.isrgbenabled
        self.buzzerControl = BuzzerControl(self.buzzerPin)
        self.buzzerControl.isenabled = self.isbuzzerenabled

    def __del__(self):
        GPIO.cleanup()

    def setupPins(self):
        GPIO.setup(self.buzzerPin, GPIO.OUT)
        GPIO.setup(self.redPin, GPIO.OUT)
        GPIO.setup(self.bluePin, GPIO.OUT)
        GPIO.setup(self.greenPin, GPIO.OUT)

