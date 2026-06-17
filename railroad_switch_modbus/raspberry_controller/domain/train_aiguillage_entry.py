from domain.aiguillage_controller import Aiguillage
from domain.packet_protocol import HallDetection, Position
from domain.train_state import Train


def handle_train_entry_detection(train: Train, aiguillage: Aiguillage) -> None:
    for sensor in aiguillage.hall_sensors.values():
        if sensor.state == HallDetection.TRAIN_WAS_DETECTED:
            if sensor.position == train.init_position:
                train.position = Position.FROG
            else:
                raise ValueError("Train is not in its init_position")
