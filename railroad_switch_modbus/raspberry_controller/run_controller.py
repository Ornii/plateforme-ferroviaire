from bootstrap.bootstrap_controller import bootstrap_controller
from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.aiguillage_controller import JunctionState
from domain.aiguillage_routing import set_aiguillage_for_train_passage
from domain.packet_protocol import Position
from domain.train_aiguillage_entry import handle_train_entry_detection
from domain.train_aiguillage_exit import handle_train_exit_detection
from domain.train_state import TrainState
from domain.verify_routing import is_routing_right
from infrastructure.aiguille.aiguille import (
    refresh_aiguille_state,
)
from infrastructure.hall_sensors.hall_sensors import (
    refresh_hall_sensors_state,
    reset_hall_sensors_state,
)

arduino = ArduinoModbusBridge(id=0x08)


train = TrainState(
    init_position=Position.TALON,
    objective_position=Position.DEVIEE,
)

if not is_routing_right(train):
    raise ValueError(
        "Wrong init_position or objective_position. The routing is impossible."
    )

aiguillage = bootstrap_controller(train, arduino)


def main(
    arduino: ArduinoModbusBridge,
    train: TrainState,
    aiguillage: JunctionState,
) -> None:
    while train.position != train.objective_position:
        refresh_hall_sensors_state(arduino, aiguillage.hall_sensors)

        refresh_aiguille_state(arduino, aiguillage.aiguillage)
        set_aiguillage_for_train_passage(arduino, train, aiguillage.aiguillage)

        if train.position == Position.FROG:
            handle_train_entry_detection(train, aiguillage)
        else:
            handle_train_exit_detection(arduino, train, aiguillage)

    reset_hall_sensors_state(arduino, aiguillage.hall_sensors)
    print("Train arrived")


if __name__ == "__main__":
    main(arduino, train, aiguillage)
