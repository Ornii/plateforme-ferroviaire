from blade_switch.blade_switch import BladeSwitch
from blade_switch.state import BladeSwitchPosition
from hall_sensors.hall_sensors import hall_sensors
from traffic_lights.state import TrafficLightColor
from traffic_lights.traffic_lights import traffic_lights


class RailroadSwitch:
    def __init__(
        self,
        blade_switch_init_position: BladeSwitchPosition,
        traffic_lights_init_color_main_track: TrafficLightColor,
        traffic_lights_init_color_straight_track: TrafficLightColor,
        traffic_lights_init_color_diverging_track: TrafficLightColor,
    ):
        self.blade_switch = BladeSwitch(blade_switch_init_position)
        self.traffic_lights = traffic_lights(
            traffic_lights_init_color_main_track,
            traffic_lights_init_color_straight_track,
            traffic_lights_init_color_diverging_track,
        )
        self.hall_sensors = hall_sensors()
