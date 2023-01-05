from src.hardware import Hardware
from src.singleton import Singleton
from threading import Thread
import RPi.GPIO as GPIO
import time

class ShutdownListener(metaclass=Singleton):

    def __init__(self):
        self.hardware = Hardware.getInstance()
        self.thread = Thread(target=self.update)
        self.thread.start()

    def update(self):
        time_flag = False
        button_flag = True
        start_time = 0
        target_time = 3
        while True:
            if GPIO.input(self.hardware.buttonPin) == GPIO.HIGH:
                if time_flag == True:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= target_time:
                        break
                if button_flag == True:
                    button_flag = False
                    time_flag = True
                    start_time = time.time()
            else:
                button_flag = True
            time.sleep(0.2)

