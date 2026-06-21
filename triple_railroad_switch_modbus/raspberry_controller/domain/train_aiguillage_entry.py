from domain.packet_protocol import HallDetection, Position
from domain.train_state import Train
from domain.triple_aiguillage_controller import TripleAiguillage


def handle_train_entry_detection(
    train: Train, triple_aiguillage: TripleAiguillage
) -> None:
    for sensor in triple_aiguillage.hall_sensors.values():
        if sensor.state == HallDetection.TRAIN_WAS_DETECTED:
            if sensor.position == train.init_position:
                train.position = Position.FROG
            else:
                raise ValueError("Train is not in its init_position")
