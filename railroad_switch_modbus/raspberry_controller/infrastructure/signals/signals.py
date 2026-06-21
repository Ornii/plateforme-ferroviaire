from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    Coil,
    Position,
    SignalColor,
)
from domain.train_state import Train

LOOP_DELAY_S = 0.05


class HallSensor:
    def __init__(self, init_color: SignalColor, position: Position) -> None:
        self.color = init_color
        self.position = position

    def get_coil(self) -> Coil:
        if self.position == Position.DEVIEE:
            return Coil.SIGNAL_DEVIEE
        elif self.position == Position.DIRECT:
            return Coil.SIGNAL_DIRECT
        else:
            return Coil.SIGNAL_TALON


def build_signals_map(
    init_color_talon: SignalColor,
    init_color_direct: SignalColor,
    init_color_deviee: SignalColor,
) -> dict[Position, HallSensor]:
    signals = {}
    signals[Position.TALON] = HallSensor(init_color_talon, Position.TALON)
    signals[Position.DIRECT] = HallSensor(init_color_direct, Position.DIRECT)
    signals[Position.DEVIEE] = HallSensor(init_color_deviee, Position.DEVIEE)
    return signals


def set_signal_color(
    arduino: ArduinoModbusBridge,
    signal: HallSensor,
    signal_color: SignalColor,
) -> None:
    signal.color = signal_color
    signal_coil = signal.get_coil()
    if signal_color == SignalColor.GREEN:
        arduino.client.write_coil(signal_coil.value, True, device_id=arduino.id)
    else:
        arduino.client.write_coil(signal_coil.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)


def set_all_signals_green(
    arduino: ArduinoModbusBridge, signals: dict[Position, HallSensor]
) -> None:
    for position in Position:
        if position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.GREEN)


def set_conflicting_signals_red(
    arduino: ArduinoModbusBridge,
    train: Train,
    signals: dict[Position, HallSensor],
):
    for position in Position:
        if position != train.position and position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.RED)
