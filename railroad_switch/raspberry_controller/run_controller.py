from bootstrap.bootstrap_controller import bootstrap_controller
from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.junction_controller import JunctionState
from domain.packet_protocol import Position
from domain.train_junction_entry import handle_train_entry_detection
from domain.train_junction_exit import handle_train_exit_detection
from domain.train_state import TrainState
from domain.verify_routing import is_routing_right
from infrastructure.hall_sensors.hall_sensors import (
    refresh_hall_sensors_state,
    reset_hall_sensors_state_of_arduino,
)

arduino = ArduinoI2cBridge(addr=0x08)
train = TrainState(
    init_position=Position.LEAD,
    objective_position=Position.REVERSE,
)

if not is_routing_right(train):
    raise ValueError(
        "Wrong init_position or objective_position. The routing is impossible."
    )

junction = bootstrap_controller(train, arduino)


def main(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    junction: JunctionState,
) -> None:
    while train.position != train.objective_position:
        refresh_hall_sensors_state(arduino, junction.hall_sensors)

        if train.position == Position.FROG:
            handle_train_entry_detection(train, junction)
        else:
            handle_train_exit_detection(arduino, train, junction)
    reset_hall_sensors_state_of_arduino(arduino)
    print("Train arrived")


if __name__ == "__main__":
    main(arduino, train, junction)
