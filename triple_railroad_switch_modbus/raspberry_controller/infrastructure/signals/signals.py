from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    Coil,
    Position,
    SignalColor,
)
from domain.train_state import Train

LOOP_DELAY_S = 0.05


class Signal:
    def __init__(self, init_color: SignalColor, position: Position) -> None:
        self.color = init_color
        self.position = position

    def get_coil(self) -> Coil:
        if self.position == Position.GAUCHE:
            return Coil.SIGNAL_GAUCHE
        elif self.position == Position.DROITE:
            return Coil.SIGNAL_DROITE
        elif self.position == Position.DIRECT:
            return Coil.SIGNAL_DIRECT
        else:
            return Coil.SIGNAL_TALON


def build_signals_map(
    init_color_talon: SignalColor,
    init_color_direct: SignalColor,
    init_color_gauche: SignalColor,
    init_color_droite: SignalColor,
) -> dict[Position, Signal]:
    signals = {}
    signals[Position.TALON] = Signal(init_color_talon, Position.TALON)
    signals[Position.DIRECT] = Signal(init_color_direct, Position.DIRECT)
    signals[Position.GAUCHE] = Signal(init_color_gauche, Position.GAUCHE)
    signals[Position.DROITE] = Signal(init_color_droite, Position.DROITE)
    return signals


def set_signal_color(
    arduino: ArduinoModbusBridge,
    signal: Signal,
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
    arduino: ArduinoModbusBridge, signals: dict[Position, Signal]
) -> None:
    for position in Position:
        if position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.GREEN)


def set_conflicting_signals_red(
    arduino: ArduinoModbusBridge,
    train: Train,
    signals: dict[Position, Signal],
):
    for position in Position:
        if position != train.position and position != Position.FROG:
            set_signal_color(arduino, signals[position], SignalColor.RED)
