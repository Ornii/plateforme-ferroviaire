from __future__ import annotations

from enum import Enum


class BladeCoil(Enum):
    BLADE_COIL = 6
    BLADE_COIL_FEEDBACK = 7


class HallCoil(Enum):
    TALON = 3
    DIRECT = 4
    DEVIEE = 5


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
