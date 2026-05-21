from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    HallCoil,
    HallDetection,
    Position,
)

LOOP_DELAY_S = 0.05


class HallSensorState:
    def __init__(self, position: Position) -> None:
        self.position = position
        self.state = HallDetection.TRAIN_NOT_DETECTED  # not detected by default


def build_hall_sensors_map() -> dict[Position, HallSensorState]:
    hall_sensors = {}
    hall_sensors[Position.TALON] = HallSensorState(Position.TALON)
    hall_sensors[Position.DIRECT] = HallSensorState(Position.DIRECT)
    hall_sensors[Position.DEVIEE] = HallSensorState(Position.DEVIEE)
    return hall_sensors


def refresh_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensorState]
) -> None:
    state_talon = arduino.client.read_coils(
        HallCoil.TALON.value, count=1, device_id=arduino.id
    )
    sleep(LOOP_DELAY_S)
    state_direct = arduino.client.read_coils(
        HallCoil.DIRECT.value, count=1, device_id=arduino.id
    )
    sleep(LOOP_DELAY_S)
    state_deviee = arduino.client.read_coils(
        HallCoil.DEVIEE.value, count=1, device_id=arduino.id
    )
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.TALON].state = HallDetection(state_talon)
    hall_sensors[Position.DIRECT].state = HallDetection(state_direct)
    hall_sensors[Position.DEVIEE].state = HallDetection(state_deviee)


def reset_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensorState]
):
    arduino.client.write_coil(HallCoil.TALON.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(HallCoil.DEVIEE.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(HallCoil.DIRECT.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.TALON].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.DIRECT].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.DEVIEE].state = HallDetection.TRAIN_NOT_DETECTED
    sleep(LOOP_DELAY_S)
