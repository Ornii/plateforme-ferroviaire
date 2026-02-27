from bootstrap.bootstrap_controller import bootstrap_controller
from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.junction_controller import JunctionState
from domain.packet_protocol import HallDetection, TrackPosition
from domain.train_state import TrainState
from infrastructure.hall_sensors.hall_sensors import refresh_hall_sensors_state
from infrastructure.signals.signals import set_all_signals_green

arduino = ArduinoI2cBridge(addr=0x08)
train = TrainState(
    init_position=TrackPosition.MAIN_TRACK,
    objective_position=TrackPosition.DIVERGING_TRACK,
)
# TODO: must verify if objective is correct (ie train can go from init_position to objective_position)


junction = bootstrap_controller(train, arduino)


def main(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    junction: JunctionState,
):
    while train.position != train.objective_position:
        refresh_hall_sensors_state(arduino, junction.hall_sensors)

        # TODO: if train is not first detected by the hallsensor located in the first position of train then raise error

        if (
            junction.hall_sensors[train.init_position].state
            == HallDetection.TRAIN_WAS_DETECTED
        ):
            train.is_in_junction = True
            # TODO: raise error if train goes to the objective position
            if (
                junction.hall_sensors[train.objective_position].state
                == HallDetection.TRAIN_WAS_DETECTED
            ):
                train.position = train.objective_position
                train.is_in_junction = False
                set_all_signals_green(arduino, junction.signals)


if __name__ == "__main__":
    main(arduino, train, junction)
