from enum import Enum

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from communication.request_response import request_packet_for_function_code
from protocol.railroad_protocol import FunctionCode, encode_get_request_packet


class TurnoutPosition(Enum):
    STRAIGHT_TRACK = 0b1
    DIVERGING_TRACK = 0b0


class TurnoutState:
    def __init__(self, init_position: TurnoutPosition):
        self.position: TurnoutPosition = init_position


def refresh_turnout_state(
    arduino: ArduinoI2cBridge, blade_switch: TurnoutState
) -> None:
    packet = request_packet_for_function_code(arduino, FunctionCode.GET_BLADE_SWITCH)
    packet_state_value = packet >> 3 & 0b1
    blade_switch.position = TurnoutPosition(packet_state_value)


def read_turnout_state(arduino: ArduinoI2cBridge) -> TurnoutPosition:
    packet = request_packet_for_function_code(arduino, FunctionCode.GET_BLADE_SWITCH)
    packet_state_value = packet >> 3 & 0b1
    return TurnoutPosition(packet_state_value)


def encode_set_turnout_packet(blade_switch_position: TurnoutPosition) -> int:
    byte = 0
    byte = byte | (blade_switch_position.value << 3)
    byte = byte | (FunctionCode.SET_BLADE_SWITCH.value << 1)
    return byte


def encode_get_turnout_packet() -> int:
    return encode_get_request_packet(FunctionCode.GET_BLADE_SWITCH)
