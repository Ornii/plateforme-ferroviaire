from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.junction_controller import JunctionState
from domain.packet_protocol import SignalColor
from domain.train_state import TrainState
from domain.turnout_routing import set_turnout_for_train_passage
from infrastructure.signals.signals import set_conflicting_signals_red
from infrastructure.turnout.turnout import (
    read_turnout_state,
    refresh_turnout_state,
)


def bootstrap_controller(train: TrainState, arduino: ArduinoI2cBridge) -> JunctionState:

    init_position_turnout = read_turnout_state(arduino)
    junction = JunctionState(
        init_position_turnout,
        SignalColor.GREEN,
        SignalColor.GREEN,
        SignalColor.GREEN,
    )

    set_conflicting_signals_red(arduino, train, junction.signals)
    refresh_turnout_state(
        arduino, junction.turnout
    )  # not necessary with init_postion_turnout
    set_turnout_for_train_passage(arduino, train, junction.turnout)
    return junction
