from time import sleep

from communication.arduino import Arduino
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
