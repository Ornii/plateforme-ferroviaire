from enum import Enum

from infrastructure.signals.signals import SignalState


class FunctionCode(Enum):
    SET_TRAFFIC_LIGHTS = 0b0
    SET_BLADE_SWITCH = 0b1
    GET_HALL_SENSORS = 0b10
    GET_BLADE_SWITCH = 0b11


class TrackPosition(Enum):
    MAIN_TRACK = 0b0
    STRAIGHT_TRACK = 0b1
    DIVERGING_TRACK = 0b10


class HallDetection(Enum):
    TRAIN_NOT_DETECTED = 0b0
    TRAIN_WAS_DETECTED = 0b1


class TurnoutPosition(Enum):
    STRAIGHT_TRACK = 0b1
    DIVERGING_TRACK = 0b0


class SignalColor(Enum):
    GREEN = 0b11
    RED = 0b0
    YELLOW = 0b10


def encode_set_turnout_packet(turnout_position: TurnoutPosition) -> int:
    byte = 0
    byte = byte | (turnout_position.value << 3)
    byte = byte | (FunctionCode.SET_BLADE_SWITCH.value << 1)
    return byte


def encode_get_request_packet(function: FunctionCode) -> int:
    byte = 0
    byte = byte | (function.value << 1)
    return byte


def encode_set_signal_packet(signal: SignalState, signal_color: SignalColor) -> int:
    byte = 0
    byte = byte | (signal.position.value << 5)
    byte = byte | (signal_color.value << 3)
    byte = byte | (FunctionCode.SET_TRAFFIC_LIGHTS.value << 1)
    return byte
