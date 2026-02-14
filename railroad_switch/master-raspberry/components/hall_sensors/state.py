from enum import Enum


class HallSensorState(Enum):
    TRAIN_NOT_DETECTED = 0b0
    TRAIN_WAS_DETECTED = 0b1
