from domain.packet_protocol import AiguillePosition, SignalColor
from infrastructure.aiguille.aiguille import AiguilleState
from infrastructure.hall_sensors.hall_sensors import build_hall_sensors_map
from infrastructure.signals.signals import build_signals_map


class JunctionState:
    def __init__(
        self,
        aiguillage_init_position: AiguillePosition,
        signals_init_color_talon: SignalColor,
        signals_init_color_direct: SignalColor,
        signals_init_color_deviee: SignalColor,
    ) -> None:
        self.aiguillage = AiguilleState(aiguillage_init_position)
        self.signals = build_signals_map(
            signals_init_color_talon,
            signals_init_color_direct,
            signals_init_color_deviee,
        )
        self.hall_sensors = build_hall_sensors_map()
