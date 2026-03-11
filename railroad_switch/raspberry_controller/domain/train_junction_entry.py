from __future__ import annotations

from domain.junction_controller import JunctionState
from domain.packet_protocol import HallDetection, Position
from domain.train_state import TrainState


def handle_train_entry_detection(train: TrainState, junction: JunctionState) -> None:
    for sensor in junction.hall_sensors.values():
        if sensor.state == HallDetection.TRAIN_WAS_DETECTED:
            if sensor.position == train.init_position:
                train.position = Position.FROG
            else:
                raise ValueError("Train is not in its init_position")
