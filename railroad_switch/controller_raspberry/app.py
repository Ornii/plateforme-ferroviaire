from bootstrap.system_initializer import initialize_controller_system
from communication.arduino_i2c_bridge import ArduinoI2cBridge
from components.hall_sensors.hall_sensors_service import (
    HallDetectionState,
    refresh_hall_sensors_state,
)
from components.traffic_lights.traffic_lights_service import (
    set_all_traffic_lights_green,
)
from domain.railroad_switch_controller import RailroadSwitchController
from domain.train_model import TrainState
from protocol.railroad_protocol import TrackPosition

arduino = ArduinoI2cBridge(addr=0x08)
train = TrainState(
    init_position=TrackPosition.MAIN_TRACK,
    objective_position=TrackPosition.DIVERGING_TRACK,
)
# TODO: must verify if objective is correct (ie train can go from init_position to objective_position)


railroad_switch = initialize_controller_system(train, arduino)


def main(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    railroad_switch: RailroadSwitchController,
):
    while train.position != train.objective_position:
        refresh_hall_sensors_state(arduino, railroad_switch.hall_sensors)

        # TODO: if train is not first detected by the hallsensor located in the first position of train then raise error

        if (
            railroad_switch.hall_sensors[train.init_position].state
            == HallDetectionState.TRAIN_WAS_DETECTED
        ):
            train.is_in_railroad_switch = True
            # TODO: raise error if train goes to the objective position
            if (
                railroad_switch.hall_sensors[train.objective_position].state
                == HallDetectionState.TRAIN_WAS_DETECTED
            ):
                train.position = train.objective_position
                train.is_in_railroad_switch = False
                set_all_traffic_lights_green(arduino, railroad_switch.traffic_lights)


if __name__ == "__main__":
    main(arduino, train, railroad_switch)
