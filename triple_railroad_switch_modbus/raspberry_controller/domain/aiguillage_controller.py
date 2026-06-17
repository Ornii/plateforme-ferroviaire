from domain.packet_protocol import AiguillePosition, AiguilleState, SignalColor
from infrastructure.aiguille.aiguille import Aiguille
from infrastructure.hall_sensors.hall_sensors import build_hall_sensors_map
from infrastructure.signals.signals import build_signals_map


class Aiguillage:
    def __init__(
        self,
        aiguille_1_init_state: AiguilleState,
        aiguille_2_init_state: AiguilleState,
        signals_init_color_talon: SignalColor,
        signals_init_color_direct: SignalColor,
        signals_init_color_gauche: SignalColor,
        signals_init_color_droite: SignalColor,
    ) -> None:
        self.aiguille_1 = Aiguille(aiguille_1_init_state, AiguillePosition.ID_1)
        self.aiguille_2 = Aiguille(aiguille_2_init_state, AiguillePosition.ID_2)
        self.signals = build_signals_map(
            signals_init_color_talon,
            signals_init_color_direct,
            signals_init_color_gauche,
            signals_init_color_droite,
        )
        self.hall_sensors = build_hall_sensors_map()
