from __future__ import annotations

from enum import Enum


class Coil(Enum):
    SIGNAL_TALON = 0
    SIGNAL_DIRECT = 1
    SIGNAL_GAUCHE = 2
    SIGNAL_DROITE = 3
    HALL_TALON = 4
    HALL_DIRECT = 5
    HALL_GAUCHE = 6
    HALL_DROITE = 7
    BLADE_1_ORDER = 8  # BLADE_1 is the nearest blade of talon position
    BLADE_1_FEEDBACK = 9
    BLADE_2_ORDER = 10
    BLADE_2_FEEDBACK = 11


class Position(Enum):
    TALON = 0
    DIRECT = 1
    GAUCHE = 2
    DROITE = 3
    FROG = 4


class AiguilleState(Enum):
    GAUCHE = 0
    DROITE = 1


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0
    TRAIN_WAS_DETECTED = 1


class SignalColor(Enum):
    GREEN = 1
    RED = 0


class AiguillePosition(Enum):
    ID_1 = 1
    ID_2 = 2
