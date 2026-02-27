from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.packet_protocol import (
    SignalColor,
    TrackPosition,
    encode_set_signal_packet,
)
from domain.train_state import TrainState


class SignalState:
    def __init__(self, init_color: SignalColor, position: TrackPosition):
        self.color = init_color
        self.position = position


def build_signals_map(
    init_color_main_track: SignalColor,
    init_color_straight_track: SignalColor,
    init_color_diverging_track: SignalColor,
) -> dict[TrackPosition, SignalState]:
    signals = {}
    signals[TrackPosition.MAIN_TRACK] = SignalState(
        init_color_main_track, TrackPosition.MAIN_TRACK
    )
    signals[TrackPosition.STRAIGHT_TRACK] = SignalState(
        init_color_straight_track, TrackPosition.STRAIGHT_TRACK
    )
    signals[TrackPosition.DIVERGING_TRACK] = SignalState(
        init_color_diverging_track, TrackPosition.DIVERGING_TRACK
    )
    return signals


def set_signal_color(
    arduino: ArduinoI2cBridge,
    signal: SignalState,
    signal_color: SignalColor,
) -> None:
    signal.color = signal_color
    packet = encode_set_signal_packet(signal, signal_color)
    arduino.bus.write_byte(arduino.addr, packet)
    sleep(0.5)


def set_all_signals_green(
    arduino: ArduinoI2cBridge, signals: dict[TrackPosition, SignalState]
):
    # SNCF requirement: all lights are green at the beginning/in the end
    for position in TrackPosition:
        set_signal_color(arduino, signals[position], SignalColor.GREEN)


def set_conflicting_signals_red(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    signals: dict[TrackPosition, SignalState],
):
    for position in TrackPosition:
        if position != train.position:
            set_signal_color(arduino, signals[position], SignalColor.RED)
