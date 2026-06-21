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
        if self.position == Position.ID_1:
            return Coil.SIGNAL_1
        elif self.position == Position.ID_2:
            return Coil.SIGNAL_2
        elif self.position == Position.ID_3:
            return Coil.SIGNAL_3
        else:
            return Coil.SIGNAL_4


def build_signals_map(
    init_color_1: SignalColor,
    init_color_2: SignalColor,
    init_color_3: SignalColor,
    init_color_4: SignalColor,
) -> dict[Position, HallSensor]:
    signals = {}
    signals[Position.ID_1] = HallSensor(init_color_1, Position.ID_1)
    signals[Position.ID_2] = HallSensor(init_color_2, Position.ID_2)
    signals[Position.ID_3] = HallSensor(init_color_3, Position.ID_3)
    signals[Position.ID_3] = HallSensor(init_color_4, Position.ID_4)
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
