from time import sleep

from communication.arduino import Arduino
from functions.encoding import packet_encode_with_get_function
from functions.state import Function


def demand_packet_with_get_function(arduino: Arduino, function: Function):
    arduino.bus.write_byte(arduino.addr, packet_encode_with_get_function(function))
    sleep(0.5)  # to avoid spamming


def receive_packet_with_get_function(arduino, function: Function) -> int:
    demand_packet_with_get_function(arduino, function)
    packet = arduino.bus.read_byte(arduino.addr)
    packet_function_value = packet >> 1 & 0b11

    while packet_function_value != function.value:
        demand_packet_with_get_function(arduino, function)
        packet = arduino.bus.read_byte(arduino.addr)
        packet_function_value = packet >> 1 & 0b11
    return packet
