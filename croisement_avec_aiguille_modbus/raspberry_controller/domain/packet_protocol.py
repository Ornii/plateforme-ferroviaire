from __future__ import annotations

from enum import Enum


class Coil(Enum):
    SIGNAL_1 = 0
    SIGNAL_2 = 1
    SIGNAL_3 = 2
    SIGNAL_4 = 3
    HALL_1 = 4
    HALL_2 = 5
    HALL_3 = 6
    HALL_4 = 7
    BLADE_ORDER = 8
    BLADE_FEEDBACK = 9


class Position(Enum):
    ID_1 = 0
    ID_2 = 1
    ID_3 = 3
    ID_4 = 4
    FROG = 5


class AiguillePosition(Enum):
    GAUCHE = 0
    DROITE = 1


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0
    TRAIN_WAS_DETECTED = 1


class SignalColor(Enum):
    GREEN = 1
    RED = 0
