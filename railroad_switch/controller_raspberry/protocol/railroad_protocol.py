from enum import Enum


class FunctionCode(Enum):
    SET_TRAFFIC_LIGHTS = 0b0
    SET_BLADE_SWITCH = 0b1
    GET_HALL_SENSORS = 0b10
    GET_BLADE_SWITCH = 0b11


class TrackPosition(Enum):
    MAIN_TRACK = 0b0
    STRAIGHT_TRACK = 0b1
    DIVERGING_TRACK = 0b10


def encode_get_request_packet(function: FunctionCode) -> int:
    byte = 0
    byte = byte | (function.value << 1)
    return byte
