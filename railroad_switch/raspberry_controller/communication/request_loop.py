from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.packet_protocol import FunctionCode, encode_get_request_packet


def request_packet_until_matching_function(
    arduino: ArduinoI2cBridge, function: FunctionCode
) -> int:
    packet_to_send = encode_get_request_packet(function)

    arduino.bus.write_byte(arduino.addr, packet_to_send)
    sleep(0.5)  # to avoid spamming

    packet = arduino.bus.read_byte(arduino.addr)
    packet_function_value = packet >> 1 & 0b11

    while packet_function_value != function.value:
        arduino.bus.write_byte(arduino.addr, packet_to_send)
        sleep(0.5)  # to avoid spamming
        packet = arduino.bus.read_byte(arduino.addr)
        packet_function_value = packet >> 1 & 0b11
    return packet
