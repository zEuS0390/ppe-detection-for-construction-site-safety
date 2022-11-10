from dataclasses import dataclass

@dataclass
class Box:
    top: int
    right: int
    bottom: int
    left: int

def isColliding(box_1: Box, box_2: Box):
    if box_1.left < box_2.right and box_1.right > box_2.left and box_1.bottom > box_2.top and box_1.top < box_2.bottom:
        return True
    return False