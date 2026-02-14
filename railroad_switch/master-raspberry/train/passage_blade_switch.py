from time import sleep

from communication.arduino import Arduino
from components.blade_switch.blade_switch import BladeSwitch
from components.blade_switch.encoding import packet_encode_set_blade_switch
from components.blade_switch.state import BladeSwitchPosition
from positions.state import Position
from train.train import Train


def set_blade_switch_with_passage(
    arduino: Arduino, train: Train, blade_switch: BladeSwitch
):

    if (
        train.objective_position == Position.STRAIGHT_TRACK
        or train.objective_position == Position.MAIN_TRACK
    ) and blade_switch.position != BladeSwitchPosition.STRAIGHT_TRACK:
        packet = packet_encode_set_blade_switch(BladeSwitchPosition.STRAIGHT_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)

    elif (
        train.objective_position == Position.DIVERGING_TRACK
        and blade_switch.position != BladeSwitchPosition.DIVERGING_TRACK
    ):
        packet = packet_encode_set_blade_switch(BladeSwitchPosition.DIVERGING_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)
