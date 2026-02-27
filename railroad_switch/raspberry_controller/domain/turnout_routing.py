from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.packet_protocol import (
    TrackPosition,
    TurnoutPosition,
    encode_set_turnout_packet,
)
from domain.train_state import TrainState
from infrastructure.turnout.turnout import TurnoutState


def set_turnout_for_train_passage(
    arduino: ArduinoI2cBridge, train: TrainState, turnout: TurnoutState
):

    if (
        train.objective_position == TrackPosition.STRAIGHT_TRACK
        or train.objective_position == TrackPosition.MAIN_TRACK
    ) and turnout.position != TurnoutPosition.STRAIGHT_TRACK:
        packet = encode_set_turnout_packet(TurnoutPosition.STRAIGHT_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)

    elif (
        train.objective_position == TrackPosition.DIVERGING_TRACK
        and turnout.position != TurnoutPosition.DIVERGING_TRACK
    ):
        packet = encode_set_turnout_packet(TurnoutPosition.DIVERGING_TRACK)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)
