from enum import Enum

# Declare constant variables for configuration and the size of the mqtt image
APP_CFG_FILE = "./cfg/app.cfg"
DEFAULT_MQTT_IMG_SIZE = [640, 480]

class Class(Enum):
    """
    The class label names arranged in order.
    """
    HELMET = 0
    NO_HELMET = 1
    GLASSES = 2
    NO_GLASSES = 3
    VEST = 4
    NO_VEST = 5
    GLOVES = 6
    NO_GLOVES = 7
    BOOTS = 8
    NO_BOOTS = 9
    PERSON = 10

class BGRColor(Enum):
    """
    The colors in BGR format. This is used for coloring 
    the bounding boxes of detected objects in the image.
    """
    RED = (0, 0, 255)
    ORANGE = (0, 165, 255)
    YELLOW = (0, 255, 255)
    GREEN = (0, 255, 0)
    SPRING_GREEN = (124, 208, 38)
    CYAN = (255, 255, 0)
    AZURE = (255, 127, 0)
    BLUE = (255, 0, 0)
    VIOLET = (128, 0, 128)
    MAGENTA = (255, 0, 255)
    ROSE = (127, 0, 255)
    BISQUE = (242, 210, 189)

class RGBColor(Enum):
    """
    The colors in RGB format with boolean values. This is 
    used for coloring the RGB LED light indicator.
    """
    RED  = (True, False, False)
    GREEN = (False, True, False)
    BLUE = (False, False, True)
    WHITE = (True, True, True)
    NONE = (False, False, False)
    YELLOW = (True, True, False)
    CYAN = (False, True, True)
    PURPLE = (True, False, True)
