from components.hall_sensors.hall_sensors_service import build_hall_sensors_map
from components.traffic_lights.traffic_lights_service import (
    SignalColor,
    build_traffic_lights_map,
)
from components.turnout.turnout_service import (
    TurnoutPosition,
    TurnoutState,
)


class RailroadSwitchController:
    def __init__(
        self,
        blade_switch_init_position: TurnoutPosition,
        traffic_lights_init_color_main_track: SignalColor,
        traffic_lights_init_color_straight_track: SignalColor,
        traffic_lights_init_color_diverging_track: SignalColor,
    ):
        self.blade_switch = TurnoutState(blade_switch_init_position)
        self.traffic_lights = build_traffic_lights_map(
            traffic_lights_init_color_main_track,
            traffic_lights_init_color_straight_track,
            traffic_lights_init_color_diverging_track,
        )
        self.hall_sensors = build_hall_sensors_map()
