from enum import Enum


class Function(Enum):
    SET_TRAFFIC_LIGHTS = 0b0
    SET_BLADE_SWITCH = 0b1
    GET_HALL_SENSORS = 0b10
    GET_BLADE_SWITCH = 0b11
