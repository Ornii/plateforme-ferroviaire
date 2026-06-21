from domain.packet_protocol import AiguillePosition, SignalColor
from infrastructure.aiguille.aiguille import Aiguille
from infrastructure.hall_sensors.hall_sensors import build_hall_sensors_map
from infrastructure.signals.signals import build_signals_map


class Aiguillage:
    def __init__(
        self,
        aiguillage_init_position: AiguillePosition,
        signals_init_color_1: SignalColor,
        signals_init_color_2: SignalColor,
        signals_init_color_3: SignalColor,
        signals_init_color_4: SignalColor,
    ) -> None:
        self.aiguillage = Aiguille(aiguillage_init_position)
        self.signals = build_signals_map(
            signals_init_color_1,
            signals_init_color_2,
            signals_init_color_3,
            signals_init_color_4,
        )
        self.hall_sensors = build_hall_sensors_map()
