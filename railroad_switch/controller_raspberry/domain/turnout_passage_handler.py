from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from components.turnout.turnout_service import (
    TurnoutPosition,
    TurnoutState,
    encode_set_turnout_packet,
)
from domain.train_model import TrainState
from protocol.railroad_protocol import TrackPosition


def set_turnout_for_train_passage(
    arduino: ArduinoI2cBridge, train: TrainState, blade_switch: TurnoutState
):

    if (
        train.objective_position == TrackPosition.STRAIGHT_TRACK
        or train.objective_position == TrackPosition.MAIN_TRACK
    ) and blade_switch.position != TurnoutPosition.STRAIGHT_TRACK:
        packet = encode_set_turnout_packet(TurnoutPosition.STRAIGHT_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)

    elif (
        train.objective_position == TrackPosition.DIVERGING_TRACK
        and blade_switch.position != TurnoutPosition.DIVERGING_TRACK
    ):
        packet = encode_set_turnout_packet(TurnoutPosition.DIVERGING_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)
