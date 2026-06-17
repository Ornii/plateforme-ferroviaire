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
    hall_sensors[Position.TALON] = HallSensor(Position.TALON)
    hall_sensors[Position.DIRECT] = HallSensor(Position.DIRECT)
    hall_sensors[Position.GAUCHE] = HallSensor(Position.GAUCHE)
    hall_sensors[Position.DROITE] = HallSensor(Position.DROITE)
    return hall_sensors


def refresh_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensor]
) -> None:
    state_talon = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_TALON.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)
    state_direct = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_DIRECT.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)
    state_gauche = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_GAUCHE.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)

    state_droite = int(
        bool(
            arduino.client.read_coils(
                Coil.HALL_DROITE.value, count=1, device_id=arduino.id
            ).bits[0]
        )
    )
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.TALON].state = HallDetection(state_talon)
    hall_sensors[Position.DIRECT].state = HallDetection(state_direct)
    hall_sensors[Position.GAUCHE].state = HallDetection(state_gauche)
    hall_sensors[Position.DROITE].state = HallDetection(state_droite)


def reset_hall_sensors_state(
    arduino: ArduinoModbusBridge, hall_sensors: dict[Position, HallSensor]
):
    arduino.client.write_coil(Coil.HALL_TALON.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_GAUCHE.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_DROITE.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)
    arduino.client.write_coil(Coil.HALL_DIRECT.value, False, device_id=arduino.id)
    sleep(LOOP_DELAY_S)

    hall_sensors[Position.TALON].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.DIRECT].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.DROITE].state = HallDetection.TRAIN_NOT_DETECTED
    hall_sensors[Position.GAUCHE].state = HallDetection.TRAIN_NOT_DETECTED
    sleep(LOOP_DELAY_S)
