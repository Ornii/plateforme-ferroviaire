from communication.arduino import Arduino
from components.blade_switch.reload_state import (
    reload_state_blade_switch,
    return_state_blade_switch,
)
from components.railroad_switch.railroad_switch import RailroadSwitch
from components.traffic_lights.change_color import change_color
from components.traffic_lights.state import TrafficLightColor
from components.traffic_lights.traffic_lights import TrafficLight
from positions.state import Position
from train.passage_blade_switch import set_blade_switch_with_passage
from train.train import Train


def all_lights_green(arduino: Arduino, traffic_lights: dict[Position, TrafficLight]):
    # SNCF requirement: all lights are green at the beginning/in the end
    for position in Position:
        change_color(arduino, traffic_lights[position], TrafficLightColor.GREEN)


def specific_lights_red(
    arduino: Arduino, train: Train, traffic_lights: dict[Position, TrafficLight]
):
    for position in Position:
        if position != train.position:
            change_color(arduino, traffic_lights[position], TrafficLightColor.RED)


def init_setup(train: Train, arduino: Arduino) -> RailroadSwitch:

    init_position_blade_switch = return_state_blade_switch(arduino)
    railroad_switch = RailroadSwitch(
        init_position_blade_switch,
        TrafficLightColor.GREEN,
        TrafficLightColor.GREEN,
        TrafficLightColor.GREEN,
    )

    specific_lights_red(arduino, train, railroad_switch.traffic_lights)
    reload_state_blade_switch(
        arduino, railroad_switch.blade_switch
    )  # not necessary with init_postion_blade_switch
    set_blade_switch_with_passage(arduino, train, railroad_switch.blade_switch)
    return railroad_switch
