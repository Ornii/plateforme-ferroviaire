from communication.arduino import Arduino
from components.hall_sensors.reload_state import reload_state_hall_sensors
from components.hall_sensors.state import HallSensorState
from components.railroad_switch.railroad_switch import RailroadSwitch
from components.traffic_lights.change_color import all_lights_green
from init.init import init_setup
from positions.state import Position
from train.train import Train

arduino = Arduino(addr=0x08)
train = Train(
    init_position=Position.MAIN_TRACK, objective_position=Position.DIVERGING_TRACK
)
# TODO: must verify if objective is correct (ie train can go from init_position to objective_position)


railroad_switch = init_setup(train, arduino)


def main(arduino: Arduino, train: Train, railroad_switch: RailroadSwitch):
    while train.position != train.objective_position:
        reload_state_hall_sensors(arduino, railroad_switch.hall_sensors)

        # TODO: if train is not first detected by the hallsensor located in the first position of train then raise error

        if (
            railroad_switch.hall_sensors[train.init_position].state
            == HallSensorState.TRAIN_WAS_DETECTED
        ):
            train.is_in_railroad_switch = True
            # TODO: raise error if train goes to the objective position
            if (
                railroad_switch.hall_sensors[train.objective_position].state
                == HallSensorState.TRAIN_WAS_DETECTED
            ):
                train.position = train.objective_position
                train.is_in_railroad_switch = False
                all_lights_green(arduino, railroad_switch.traffic_lights)


if __name__ == "__main__":
    main(arduino, train, railroad_switch)
