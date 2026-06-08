from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import AiguillePosition, BladeCoil


class AiguilleState:
    def __init__(self, init_position: AiguillePosition) -> None:
        self.position: AiguillePosition = init_position


def refresh_aiguille_state(
    arduino: ArduinoModbusBridge, aiguille: AiguilleState
) -> None:
    aiguille.position = read_aiguille_state(arduino)


def read_aiguille_state(arduino: ArduinoModbusBridge) -> AiguillePosition:
    result = arduino.client.read_coils(
        BladeCoil.FEEDBACK.value, count=1, device_id=arduino.id
    )
    return AiguillePosition(int(bool(result.bits[0])))
