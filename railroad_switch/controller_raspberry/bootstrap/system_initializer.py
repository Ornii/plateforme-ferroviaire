from communication.arduino_i2c_bridge import ArduinoI2cBridge
from components.traffic_lights.traffic_lights_service import (
    SignalColor,
    set_non_train_traffic_lights_red,
)
from components.turnout.turnout_service import read_turnout_state, refresh_turnout_state
from domain.railroad_switch_controller import RailroadSwitchController
from domain.train_model import TrainState
from domain.turnout_passage_handler import set_turnout_for_train_passage


def initialize_controller_system(
    train: TrainState, arduino: ArduinoI2cBridge
) -> RailroadSwitchController:

    init_position_blade_switch = read_turnout_state(arduino)
    railroad_switch = RailroadSwitchController(
        init_position_blade_switch,
        SignalColor.GREEN,
        SignalColor.GREEN,
        SignalColor.GREEN,
    )

    set_non_train_traffic_lights_red(arduino, train, railroad_switch.traffic_lights)
    refresh_turnout_state(
        arduino, railroad_switch.blade_switch
    )  # not necessary with init_postion_blade_switch
    set_turnout_for_train_passage(arduino, train, railroad_switch.blade_switch)
    return railroad_switch
