from blade_switch.blade_switch import BladeSwitch
from blade_switch.state import BladeSwitchPosition
from communication.arduino import Arduino
from communication.receive import receive_packet_with_get_function
from functions.state import Function


def reload_state_blade_switch(arduino: Arduino, blade_switch: BladeSwitch) -> None:
    packet = receive_packet_with_get_function(arduino, Function.GET_BLADE_SWITCH)
    packet_state_value = packet >> 3 & 0b1
    blade_switch.position = BladeSwitchPosition(packet_state_value)


def return_state_blade_switch(arduino: Arduino) -> BladeSwitchPosition:
    packet = receive_packet_with_get_function(arduino, Function.GET_BLADE_SWITCH)
    packet_state_value = packet >> 3 & 0b1
    return BladeSwitchPosition(packet_state_value)
