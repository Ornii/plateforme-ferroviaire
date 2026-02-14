from hall_sensors.state import HallSensorState
from positions.state import Position


class HallSensor:
    def __init__(self, position: Position):
        self.position = position
        self.state = HallSensorState.TRAIN_NOT_DETECTED  # not detected by default


def hall_sensors() -> dict[Position, HallSensor]:
    hall_sensors = {}
    hall_sensors[Position.MAIN_TRACK] = HallSensor(Position.MAIN_TRACK)
    hall_sensors[Position.STRAIGHT_TRACK] = HallSensor(Position.STRAIGHT_TRACK)
    hall_sensors[Position.DIVERGING_TRACK] = HallSensor(Position.DIVERGING_TRACK)
    return hall_sensors
