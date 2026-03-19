from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from communication.request_loop import request_packet_until_matching_function
from domain.packet_protocol import (
    Function,
    HallDetection,
    Position,
    encode_get_request_packet,
)


class HallSensorState:
    def __init__(self, position: Position) -> None:
        self.position = position
        self.state = HallDetection.TRAIN_NOT_DETECTED  # not detected by default


def build_hall_sensors_map() -> dict[Position, HallSensorState]:
    hall_sensors = {}
    hall_sensors[Position.LEAD] = HallSensorState(Position.LEAD)
    hall_sensors[Position.NORMAL] = HallSensorState(Position.NORMAL)
    hall_sensors[Position.REVERSE] = HallSensorState(Position.REVERSE)
    return hall_sensors


def encode_get_hall_sensors_packet() -> int:
    return encode_get_request_packet(Function.GET_HALL_SENSORS)


def refresh_hall_sensors_state(
    arduino: ArduinoI2cBridge, hall_sensors: dict[Position, HallSensorState]
) -> None:
    packet = request_packet_until_matching_function(
        arduino, Function.GET_HALL_SENSORS, Function.RECEIVED_HALL_SENSORS
    )

    packet_state_main_track = packet >> 5 & 0b1
    packet_state_straight_track = packet >> 4 & 0b1
    packet_state_diverging_track = packet >> 3 & 0b1

    hall_sensors[Position.LEAD].state = HallDetection(packet_state_main_track)
    hall_sensors[Position.NORMAL].state = HallDetection(packet_state_straight_track)
    hall_sensors[Position.REVERSE].state = HallDetection(packet_state_diverging_track)


def reset_hall_sensors_state_of_arduino(arduino: ArduinoI2cBridge):
    packet = encode_get_request_packet(Function.RESET_HALL_SENSORS)
    arduino.bus.write_byte(arduino.addr, packet)
    sleep(0.5)  # to avoid spamming
