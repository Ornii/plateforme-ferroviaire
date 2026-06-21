from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import AiguillePosition, SignalColor
from domain.train_state import Train
from domain.triple_aiguillage_controller import TripleAiguillage
from domain.triple_aiguillage_routing import set_aiguilles_for_train_passage
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
    train: Train, arduino: ArduinoModbusBridge
) -> TripleAiguillage:
    init_position_aiguille_1 = read_aiguille_state(arduino, AiguillePosition.ID_1)
    init_position_aiguille_2 = read_aiguille_state(arduino, AiguillePosition.ID_2)
    triple_aiguillage = TripleAiguillage(
        init_position_aiguille_1,
        init_position_aiguille_2,
        SignalColor.GREEN,
        SignalColor.GREEN,
        SignalColor.GREEN,
        SignalColor.GREEN,
    )
    set_all_signals_green(arduino, triple_aiguillage.signals)
    set_conflicting_signals_red(arduino, train, triple_aiguillage.signals)

    refresh_aiguille_state(
        arduino, triple_aiguillage.aiguille_1
    )  # not necessary with init_position_triple_aiguillage_1
    refresh_aiguille_state(
        arduino, triple_aiguillage.aiguille_2
    )  # not necessary with init_position_triple_aiguillage_2

    set_aiguilles_for_train_passage(
        arduino, train, triple_aiguillage.aiguille_1, triple_aiguillage.aiguille_2
    )

    reset_hall_sensors_state(arduino, triple_aiguillage.hall_sensors)
    return triple_aiguillage
