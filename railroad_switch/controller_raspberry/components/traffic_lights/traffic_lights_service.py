from enum import Enum
from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.train_model import TrainState
from protocol.railroad_protocol import FunctionCode, TrackPosition


class SignalColor(Enum):
    GREEN = 0b11
    RED = 0b0
    YELLOW = 0b10


class TrafficLightState:
    def __init__(self, init_color: SignalColor, position: TrackPosition):
        self.color = init_color
        self.position = position


def encode_set_traffic_light_packet(
    traffic_light: TrafficLightState, traffic_light_color: SignalColor
) -> int:
    byte = 0
    byte = byte | (traffic_light.position.value << 5)
    byte = byte | (traffic_light_color.value << 3)
    byte = byte | (FunctionCode.SET_TRAFFIC_LIGHTS.value << 1)
    return byte


def build_traffic_lights_map(
    init_color_main_track: SignalColor,
    init_color_straight_track: SignalColor,
    init_color_diverging_track: SignalColor,
) -> dict[TrackPosition, TrafficLightState]:
    traffic_lights = {}
    traffic_lights[TrackPosition.MAIN_TRACK] = TrafficLightState(
        init_color_main_track, TrackPosition.MAIN_TRACK
    )
    traffic_lights[TrackPosition.STRAIGHT_TRACK] = TrafficLightState(
        init_color_straight_track, TrackPosition.STRAIGHT_TRACK
    )
    traffic_lights[TrackPosition.DIVERGING_TRACK] = TrafficLightState(
        init_color_diverging_track, TrackPosition.DIVERGING_TRACK
    )
    return traffic_lights


def set_traffic_light_color(
    arduino: ArduinoI2cBridge,
    traffic_light: TrafficLightState,
    traffic_light_color: SignalColor,
) -> None:
    traffic_light.color = traffic_light_color
    packet = encode_set_traffic_light_packet(traffic_light, traffic_light_color)
    arduino.bus.write_byte(arduino.addr, packet)
    sleep(0.5)


def set_all_traffic_lights_green(
    arduino: ArduinoI2cBridge, traffic_lights: dict[TrackPosition, TrafficLightState]
):
    # SNCF requirement: all lights are green at the beginning/in the end
    for position in TrackPosition:
        set_traffic_light_color(arduino, traffic_lights[position], SignalColor.GREEN)


def set_non_train_traffic_lights_red(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    traffic_lights: dict[TrackPosition, TrafficLightState],
):
    for position in TrackPosition:
        if position != train.position:
            set_traffic_light_color(arduino, traffic_lights[position], SignalColor.RED)
