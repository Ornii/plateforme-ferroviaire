from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import AiguillePosition, AiguilleState, Coil


class Aiguille:
    def __init__(self, init_state: AiguilleState, position: AiguillePosition) -> None:
        self.state: AiguilleState = init_state
        self.position = position


def refresh_aiguille_state(arduino: ArduinoModbusBridge, aiguille: Aiguille) -> None:
    aiguille.state = read_aiguille_state(arduino, aiguille.position)


def read_aiguille_state(
    arduino: ArduinoModbusBridge, position: AiguillePosition
) -> AiguilleState:
    if position == AiguillePosition.ID_1:
        result = arduino.client.read_coils(
            Coil.BLADE_1_FEEDBACK.value, count=1, device_id=arduino.id
        )
    else:
        result = arduino.client.read_coils(
            Coil.BLADE_2_FEEDBACK.value, count=1, device_id=arduino.id
        )
    return AiguilleState(int(bool(result.bits[0])))
