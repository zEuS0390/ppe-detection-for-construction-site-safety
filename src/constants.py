from enum import Enum

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

class Color(Enum):
    """
    Color in BGR format
    """
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)