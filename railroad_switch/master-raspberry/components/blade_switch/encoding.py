from blade_switch.state import BladeSwitchPosition
from functions.encoding import packet_encode_with_get_function
from functions.state import Function


def packet_encode_set_blade_switch(blade_switch_position: BladeSwitchPosition) -> int:
    byte = 0
    byte = byte | (blade_switch_position.value << 3)
    byte = byte | (Function.SET_BLADE_SWITCH.value << 1)
    return byte


def packet_encode_get_blade_switch() -> int:
    return packet_encode_with_get_function(Function.GET_BLADE_SWITCH)
