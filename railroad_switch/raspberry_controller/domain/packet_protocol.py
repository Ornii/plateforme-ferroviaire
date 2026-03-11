from __future__ import annotations

from enum import Enum

from infrastructure.signals.signals import SignalState


class Function(Enum):
    SET_TRAFFIC_LIGHTS = 0b00
    SET_TURNOUT = 0b01
    GET_HALL_SENSORS = 0b10
    GET_TURNOUT = 0b11


class Position(Enum):
    LEAD = 0b00
    NORMAL = 0b01
    REVERSE = 0b10
    FROG = 0b11


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0b0
    TRAIN_WAS_DETECTED = 0b1


class TurnoutPosition(Enum):
    NORMAL = 0b1
    REVERSE = 0b0


class SignalColor(Enum):
    GREEN = 0b11
    RED = 0b00
    YELLOW = 0b10


def encode_set_turnout_packet(turnout_position: TurnoutPosition) -> int:
    byte = 0
    byte = byte | (turnout_position.value << 3)
    byte = byte | (Function.SET_TURNOUT.value << 1)
    return byte


def encode_get_request_packet(function: Function) -> int:
    byte = 0
    byte = byte | (function.value << 1)
    return byte


def encode_set_signal_packet(signal: SignalState, signal_color: SignalColor) -> int:
    byte = 0
    byte = byte | (signal.position.value << 5)
    byte = byte | (signal_color.value << 3)
    byte = byte | (Function.SET_TRAFFIC_LIGHTS.value << 1)
    return byte
