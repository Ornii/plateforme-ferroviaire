from enum import Enum


class Position(Enum):
    MAIN_TRACK = 0b0
    STRAIGHT_TRACK = 0b1
    DIVERGING_TRACK = 0b10
