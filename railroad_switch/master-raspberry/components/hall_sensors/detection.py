from components.hall_sensors.state import HallSensorState
from hall_sensors.hall_sensors import HallSensor
from positions.state import Position


def is_train_detected(
    hall_sensors: dict[Position, HallSensor], position: Position
) -> bool:

    return hall_sensors[position].state == HallSensorState.TRAIN_WAS_DETECTED


# REMOVE THIS FILE (useless)
