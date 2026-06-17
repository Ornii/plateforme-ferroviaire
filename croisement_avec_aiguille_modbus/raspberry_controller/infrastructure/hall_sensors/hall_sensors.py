from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import Coil, HallDetection, Position

LOOP_DELAY_S = 0.05


class HallSensor:
    def __init__(self, position: Position) -> None:
        self.position = position
        self.state = HallDetection.TRAIN_NOT_DETECTED


def build_hall_sensors_map() -> dict[Position, HallSensor]:
    hall_sensors = {}
    hall_sensors[Position.ID_1] = HallSensor(Position.ID_1)
    hall_sensors[Position.ID_2] = HallSensor(Position.ID_2)
    hall_sensors[Position.ID_3] = HallSensor(Position.ID_3)
    hall_sensors[Position.ID_4] = HallSensor(Position.ID_4)
    return hall_sensors


def refresh_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensor]
) -> None:
    state_1 = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_1.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)
    state_2 = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_2.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)
    state_3 = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_3.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)
    state_4 = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_4.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.ID_1].state = HallDetection(state_1)
    hall_sensors[Position.ID_2].state = HallDetection(state_2)
    hall_sensors[Position.ID_3].state = HallDetection(state_3)
    hall_sensors[Position.ID_4].state = HallDetection(state_4)


def reset_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensor]
):
    arduino.client.write_coil(Coil.HALL_1.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_2.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_3.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_4.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.ID_1].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.ID_2].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.ID_3].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.ID_4].state = HallDetection.TRAIN_NOT_DETECTED
    sleep(LOOP_DELAY_S)
