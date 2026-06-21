from __future__ import annotations

from enum import Enum


class Coil(Enum):
    SIGNAL_TALON = 0
    SIGNAL_DIRECT = 1
    SIGNAL_DEVIEE = 2
    HALL_TALON = 3
    HALL_DIRECT = 4
    HALL_DEVIEE = 5
    BLADE_ORDER = 6
    BLADE_FEEDBACK = 7


class Position(Enum):
    TALON = 0
    DIRECT = 1
    DEVIEE = 2
    FROG = 3


class AiguillePosition(Enum):
    DEVIEE = 0
    DIRECT = 1


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0
    TRAIN_WAS_DETECTED = 1


class SignalColor(Enum):
    GREEN = 1
    RED = 0
