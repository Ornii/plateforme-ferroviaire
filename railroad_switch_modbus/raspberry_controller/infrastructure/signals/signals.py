from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    Position,
    SignalCoil,
    SignalColor,
)
from domain.train_state import TrainState

LOOP_DELAY_S = 0.05


class SignalState:
    def __init__(self, init_color: SignalColor, position: Position) -> None:
        self.color = init_color
        self.position = position

    def get_coil(self) -> SignalCoil:
        if self.position == Position.DEVIEE:
            return SignalCoil.DEVIEE
        elif self.position == Position.DIRECT:
            return SignalCoil.DIRECT
        else:
            return SignalCoil.TALON


def build_signals_map(
    init_color_talon: SignalColor,
    init_color_direct: SignalColor,
    init_color_deviee: SignalColor,
) -> dict[Position, SignalState]:
    signals = {}
    signals[Position.TALON] = SignalState(init_color_talon, Position.TALON)
    signals[Position.DIRECT] = SignalState(init_color_direct, Position.DIRECT)
    signals[Position.DEVIEE] = SignalState(init_color_deviee, Position.DEVIEE)
    return signals


def set_signal_color(
    arduino: ArduinoModbusBridge,
    signal: SignalState,
    signal_color: SignalColor,
) -> None:
    signal.color = signal_color
    signal_coil = signal.get_coil()
    arduino.client.write_coil(signal_coil.value, True, device_id=arduino.id)
    sleep(LOOP_DELAY_S)


def set_all_signals_green(
    arduino: ArduinoModbusBridge, signals: dict[Position, SignalState]
) -> None:
    for position in Position:
        if position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.GREEN)


def set_conflicting_signals_red(
    arduino: ArduinoModbusBridge,
    train: TrainState,
    signals: dict[Position, SignalState],
):
    for position in Position:
        if position != train.position and position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.RED)
