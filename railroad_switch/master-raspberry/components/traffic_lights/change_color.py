from time import sleep

from communication.arduino import Arduino
from positions.state import Position
from traffic_lights.encoding import packet_encode_set_traffic_lights
from traffic_lights.state import TrafficLightColor
from traffic_lights.traffic_lights import TrafficLight


def change_color(
    arduino: Arduino,
    traffic_light: TrafficLight,
    traffic_light_color: TrafficLightColor,
) -> None:
    traffic_light.color = traffic_light_color
    packet = packet_encode_set_traffic_lights(traffic_light, traffic_light_color)
    arduino.bus.write_byte(arduino.addr, packet)
    sleep(0.5)


def all_lights_green(arduino: Arduino, traffic_lights: dict[Position, TrafficLight]):
    # SNCF requirement: all lights are green at the beginning/in the end
    for position in Position:
        change_color(arduino, traffic_lights[position], TrafficLightColor.GREEN)


def specific_lights_red(
    arduino: Arduino, train: Train, traffic_lights: dict[Position, TrafficLight]
):
    for position in Position:
        if position != train.position:
            change_color(arduino, traffic_lights[position], TrafficLightColor.RED)
