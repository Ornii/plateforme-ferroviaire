from domain.junction_controller import JunctionState
from domain.packet_protocol import HallDetection
from domain.train_state import TrainState


def handle_train_entry_detection(train: TrainState, junction: JunctionState):
    for sensor in junction.hall_sensors.values():
        if sensor.state == HallDetection.TRAIN_WAS_DETECTED:
            if sensor.position == train.init_position:
                train.is_in_junction = True
            else:
                raise ValueError("Train is not in its init_position")
