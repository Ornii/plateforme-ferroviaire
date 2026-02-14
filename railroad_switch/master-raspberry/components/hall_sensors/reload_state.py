from communication.arduino import Arduino
from communication.receive import receive_packet_with_get_function
from functions.state import Function
from hall_sensors.hall_sensors import HallSensor
from hall_sensors.state import HallSensorState
from positions.state import Position


def reload_state_hall_sensors(
    arduino: Arduino, hall_sensors: dict[Position, HallSensor]
) -> None:
    packet = receive_packet_with_get_function(arduino, Function.GET_HALL_SENSORS)

    packet_state_main_track = packet >> 5 & 0b1
    packet_state_straight_track = packet >> 4 & 0b1
    packet_state_diverging_track = packet >> 3 & 0b1

    hall_sensors[Position.MAIN_TRACK].state = HallSensorState(packet_state_main_track)
    hall_sensors[Position.STRAIGHT_TRACK].state = HallSensorState(
        packet_state_straight_track
    )
    hall_sensors[Position.DIVERGING_TRACK].state = HallSensorState(
        packet_state_diverging_track
    )
