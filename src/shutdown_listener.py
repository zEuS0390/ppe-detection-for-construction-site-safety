from src.hardware import Hardware
from src.singleton import Singleton
from threading import Thread
import time
try:
    import RPi.GPIO as GPIO
    class ShutdownListener(metaclass=Singleton):

        def __init__(self):
            self.isRunning = True
            self.hardware = Hardware.getInstance()
            self.thread = Thread(target=self.update)
            self.thread.start()

        def wait(self):
            try:
                while self.isRunning: time.sleep(1)
            except KeyboardInterrupt:
                self.isRunning = False
            self.thread.join()

        def update(self):
            time_flag = False
            button_flag = True
            start_time = 0
            target_time = 3
            while self.isRunning:
                if GPIO.input(self.hardware.buttonPin) == GPIO.HIGH:
                    if time_flag == True:
                        elapsed_time = time.time() - start_time
                        if elapsed_time >= target_time:
                            self.isRunning = False
                    if button_flag == True:
                        button_flag = False
                        time_flag = True
                        start_time = time.time()
                else:
                    button_flag = True
                time.sleep(0.1)
# Create a different form of ShutdownListener if the import error occurs
except ImportError:
    class ShutdownListener(metaclass=Singleton):

        def __init__(self):
            self.isRunning = True
            
        def wait(self):
            try:
                while self.isRunning: time.sleep(1)
            except KeyboardInterrupt:
                self.isRunning = False

        def update(self): ...
