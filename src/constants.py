from enum import Enum

APP_CFG_FILE = "./cfg/app.cfg"
DEFAULT_MQTT_IMG_SIZE = [640, 480]

class Class(Enum):
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
    Color in BGR format
    """
    RED = (0, 0, 255)                   # 0
    ORANGE = (0, 165, 255)              # 1
    YELLOW = (0, 255, 255)              # 2
    GREEN = (0, 255, 0)                 # 3
    SPRING_GREEN = (124, 208, 38)       # 4
    CYAN = (255, 255, 0)                # 5
    AZURE = (255, 127, 0)               # 6
    BLUE = (255, 0, 0)                  # 7
    VIOLET = (128, 0, 128)              # 8
    MAGENTA = (255, 0, 255)             # 9
    ROSE = (127, 0, 255)                # 10
    BISQUE = (242, 210, 189)            # 11

class RGBColor(Enum):
    """
    Color in RGB format
    """
    RED  = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    NONE = (0, 0, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    PURPLE = (255, 0, 255)
