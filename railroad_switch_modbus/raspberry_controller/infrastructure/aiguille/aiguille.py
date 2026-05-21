from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import BLADE_COIL, AiguillePosition


class AiguilleState:
    def __init__(self, init_position: AiguillePosition) -> None:
        self.position: AiguillePosition = init_position


def refresh_aiguille_state(
    arduino: ArduinoModbusBridge, aiguille: AiguilleState
) -> None:
    state_aiguille = arduino.client.read_coils(
        BLADE_COIL, count=1, device_id=arduino.id
    )
    aiguille.position = AiguillePosition(state_aiguille)


def read_aiguille_state(arduino: ArduinoModbusBridge) -> AiguillePosition:
    result = arduino.client.read_coils(BLADE_COIL, count=1, device_id=arduino.id)
    return AiguillePosition(result)
