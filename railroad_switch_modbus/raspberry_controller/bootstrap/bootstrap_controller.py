from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.aiguillage_controller import JunctionState
from domain.aiguillage_routing import set_aiguillage_for_train_passage
from domain.packet_protocol import SignalColor
from domain.train_state import TrainState
from infrastructure.aiguille.aiguille import (
    read_aiguille_state,
    refresh_aiguille_state,
)
from infrastructure.hall_sensors.hall_sensors import reset_hall_sensors_state
from infrastructure.signals.signals import (
    set_all_signals_green,
    set_conflicting_signals_red,
)


def bootstrap_controller(
    train: TrainState, arduino: ArduinoModbusBridge
) -> JunctionState:
    init_position_aiguillage = read_aiguille_state(arduino)
    aiguillage = JunctionState(
        init_position_aiguillage,
        SignalColor.GREEN,
        SignalColor.GREEN,
        SignalColor.GREEN,
    )
    set_all_signals_green(arduino, aiguillage.signals)
    set_conflicting_signals_red(arduino, train, aiguillage.signals)

    refresh_aiguille_state(
        arduino, aiguillage.aiguillage
    )  # not necessary with init_position_aiguillage
    set_aiguillage_for_train_passage(arduino, train, aiguillage.aiguillage)

    reset_hall_sensors_state(arduino, aiguillage.hall_sensors)
    return aiguillage
