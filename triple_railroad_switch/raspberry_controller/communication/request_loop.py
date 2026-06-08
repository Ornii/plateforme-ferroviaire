from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.packet_protocol import Function, encode_get_request_packet

LOOP_DELAY_S = 0.05


def request_packet_until_matching_function(
    arduino: ArduinoI2cBridge, get_function: Function, received_function
) -> int:
    packet_to_send = encode_get_request_packet(get_function)

    arduino.bus.write_byte(arduino.addr, packet_to_send)
    sleep(LOOP_DELAY_S)

    packet = arduino.bus.read_byte(arduino.addr)
    packet_function_value = packet & 0b111

    while packet_function_value != received_function.value:
        arduino.bus.write_byte(arduino.addr, packet_to_send)
        sleep(LOOP_DELAY_S)
        packet = arduino.bus.read_byte(arduino.addr)
        packet_function_value = packet & 0b111
    return packet
