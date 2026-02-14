from functions.state import Function
from traffic_lights.state import TrafficLightColor
from traffic_lights.traffic_lights import TrafficLight


def packet_encode_set_traffic_lights(
    traffic_light: TrafficLight, traffic_light_color: TrafficLightColor
) -> int:
    byte = 0
    byte = byte | (traffic_light.position.value << 5)
    byte = byte | (traffic_light_color.value << 3)
    byte = byte | (Function.SET_TRAFFIC_LIGHTS.value << 1)
    return byte
