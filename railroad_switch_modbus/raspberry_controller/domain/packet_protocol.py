from __future__ import annotations

from enum import Enum, auto

BLADE_COIL = auto()


class HallCoil(Enum):
    DEVIEE = auto()
    DIRECT = auto()
    TALON = auto()


class SignalCoil(Enum):
    DEVIEE = auto()
    DIRECT = auto()
    TALON = auto()


class Position(Enum):
    TALON = auto()
    DIRECT = auto()
    DEVIEE = auto()
    FROG = auto()


class AiguillePosition(Enum):
    DEVIEE = 0
    DIRECT = 1


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0
    TRAIN_WAS_DETECTED = 1


class SignalColor(Enum):
    GREEN = 1
    RED = 0
