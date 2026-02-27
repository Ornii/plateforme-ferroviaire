from domain.packet_protocol import SignalColor, TurnoutPosition
from infrastructure.hall_sensors.hall_sensors import build_hall_sensors_map
from infrastructure.signals.signals import build_signals_map
from infrastructure.turnout.turnout import TurnoutState


class JunctionState:
    def __init__(
        self,
        turnout_init_position: TurnoutPosition,
        signals_init_color_main_track: SignalColor,
        signals_init_color_straight_track: SignalColor,
        signals_init_color_diverging_track: SignalColor,
    ):
        self.turnout = TurnoutState(turnout_init_position)
        self.signals = build_signals_map(
            signals_init_color_main_track,
            signals_init_color_straight_track,
            signals_init_color_diverging_track,
        )
        self.hall_sensors = build_hall_sensors_map()
