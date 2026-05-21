from __future__ import annotations

from enum import Enum


BLADE_COIL = 3


class HallCoil(Enum):
    TALON = 4
    DIRECT = 5
    DEVIEE = 6


class SignalCoil(Enum):
    TALON = 0
    DIRECT = 1
    DEVIEE = 2


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
