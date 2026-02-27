from communication.arduino_i2c_bridge import ArduinoI2cBridge
from communication.request_loop import request_packet_until_matching_function
from domain.packet_protocol import FunctionCode, TurnoutPosition


class TurnoutState:
    def __init__(self, init_position: TurnoutPosition):
        self.position: TurnoutPosition = init_position


def refresh_turnout_state(arduino: ArduinoI2cBridge, turnout: TurnoutState) -> None:
    packet = request_packet_until_matching_function(
        arduino, FunctionCode.GET_BLADE_SWITCH
    )
    packet_state_value = packet >> 3 & 0b1
    turnout.position = TurnoutPosition(packet_state_value)


def read_turnout_state(arduino: ArduinoI2cBridge) -> TurnoutPosition:
    packet = request_packet_until_matching_function(
        arduino, FunctionCode.GET_BLADE_SWITCH
    )
    packet_state_value = packet >> 3 & 0b1
    return TurnoutPosition(packet_state_value)
