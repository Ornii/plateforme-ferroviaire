from components.traffic_lights.state import TrafficLightColor
from positions.state import Position


class TrafficLight:
    def __init__(self, init_color: TrafficLightColor, position: Position):
        self.color = init_color
        self.position = position


def traffic_lights(
    init_color_main_track: TrafficLightColor,
    init_color_straight_track: TrafficLightColor,
    init_color_diverging_track: TrafficLightColor,
) -> dict[Position, TrafficLight]:
    traffic_lights = {}
    traffic_lights[Position.MAIN_TRACK] = TrafficLight(
        init_color_main_track, Position.MAIN_TRACK
    )
    traffic_lights[Position.STRAIGHT_TRACK] = TrafficLight(
        init_color_straight_track, Position.STRAIGHT_TRACK
    )
    traffic_lights[Position.DIVERGING_TRACK] = TrafficLight(
        init_color_diverging_track, Position.DIVERGING_TRACK
    )
    return traffic_lights
