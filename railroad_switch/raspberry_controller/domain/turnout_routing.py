from __future__ import annotations

from time import sleep

from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.packet_protocol import (
    Position,
    TurnoutPosition,
    encode_set_turnout_packet,
)
from domain.train_state import TrainState
from infrastructure.turnout.turnout import TurnoutState


def set_turnout_for_train_passage(
    arduino: ArduinoI2cBridge, train: TrainState, turnout: TurnoutState
) -> None:

    if (
        train.objective_position == Position.NORMAL
        or train.objective_position == Position.LEAD
    ) and turnout.position != TurnoutPosition.NORMAL:
        packet = encode_set_turnout_packet(TurnoutPosition.NORMAL)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)

    elif (
        train.objective_position == Position.REVERSE
        and turnout.position != TurnoutPosition.REVERSE
    ):
        packet = encode_set_turnout_packet(TurnoutPosition.REVERSE)
        arduino.bus.write_byte(arduino.addr, packet)
        sleep(0.5)
