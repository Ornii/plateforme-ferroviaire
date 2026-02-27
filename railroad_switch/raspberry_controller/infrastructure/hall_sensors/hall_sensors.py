from communication.arduino_i2c_bridge import ArduinoI2cBridge
from communication.request_loop import request_packet_until_matching_function
from domain.packet_protocol import (
    FunctionCode,
    HallDetection,
    TrackPosition,
    encode_get_request_packet,
)


class HallSensorState:
    def __init__(self, position: TrackPosition):
        self.position = position
        self.state = HallDetection.TRAIN_NOT_DETECTED  # not detected by default


def build_hall_sensors_map() -> dict[TrackPosition, HallSensorState]:
    hall_sensors = {}
    hall_sensors[TrackPosition.MAIN_TRACK] = HallSensorState(TrackPosition.MAIN_TRACK)
    hall_sensors[TrackPosition.STRAIGHT_TRACK] = HallSensorState(
        TrackPosition.STRAIGHT_TRACK
    )
    hall_sensors[TrackPosition.DIVERGING_TRACK] = HallSensorState(
        TrackPosition.DIVERGING_TRACK
    )
    return hall_sensors


def encode_get_hall_sensors_packet() -> int:
    return encode_get_request_packet(FunctionCode.GET_HALL_SENSORS)


def refresh_hall_sensors_state(
    arduino: ArduinoI2cBridge, hall_sensors: dict[TrackPosition, HallSensorState]
) -> None:
    packet = request_packet_until_matching_function(
        arduino, FunctionCode.GET_HALL_SENSORS
    )

    packet_state_main_track = packet >> 5 & 0b1
    packet_state_straight_track = packet >> 4 & 0b1
    packet_state_diverging_track = packet >> 3 & 0b1

    hall_sensors[TrackPosition.MAIN_TRACK].state = HallDetection(
        packet_state_main_track
    )
    hall_sensors[TrackPosition.STRAIGHT_TRACK].state = HallDetection(
        packet_state_straight_track
    )
    hall_sensors[TrackPosition.DIVERGING_TRACK].state = HallDetection(
        packet_state_diverging_track
    )
