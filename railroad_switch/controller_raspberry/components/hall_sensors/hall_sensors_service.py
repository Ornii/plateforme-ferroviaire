from enum import Enum

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from communication.request_response import request_packet_for_function_code
from protocol.railroad_protocol import (
    FunctionCode,
    TrackPosition,
    encode_get_request_packet,
)


class HallDetectionState(Enum):
    TRAIN_NOT_DETECTED = 0b0
    TRAIN_WAS_DETECTED = 0b1


class HallSensorStateEntry:
    def __init__(self, position: TrackPosition):
        self.position = position
        self.state = HallDetectionState.TRAIN_NOT_DETECTED  # not detected by default


def build_hall_sensors_map() -> dict[TrackPosition, HallSensorStateEntry]:
    hall_sensors = {}
    hall_sensors[TrackPosition.MAIN_TRACK] = HallSensorStateEntry(
        TrackPosition.MAIN_TRACK
    )
    hall_sensors[TrackPosition.STRAIGHT_TRACK] = HallSensorStateEntry(
        TrackPosition.STRAIGHT_TRACK
    )
    hall_sensors[TrackPosition.DIVERGING_TRACK] = HallSensorStateEntry(
        TrackPosition.DIVERGING_TRACK
    )
    return hall_sensors


def encode_get_hall_sensors_packet() -> int:
    return encode_get_request_packet(FunctionCode.GET_HALL_SENSORS)


def refresh_hall_sensors_state(
    arduino: ArduinoI2cBridge, hall_sensors: dict[TrackPosition, HallSensorStateEntry]
) -> None:
    packet = request_packet_for_function_code(arduino, FunctionCode.GET_HALL_SENSORS)

    packet_state_main_track = packet >> 5 & 0b1
    packet_state_straight_track = packet >> 4 & 0b1
    packet_state_diverging_track = packet >> 3 & 0b1

    hall_sensors[TrackPosition.MAIN_TRACK].state = HallDetectionState(
        packet_state_main_track
    )
    hall_sensors[TrackPosition.STRAIGHT_TRACK].state = HallDetectionState(
        packet_state_straight_track
    )
    hall_sensors[TrackPosition.DIVERGING_TRACK].state = HallDetectionState(
        packet_state_diverging_track
    )
