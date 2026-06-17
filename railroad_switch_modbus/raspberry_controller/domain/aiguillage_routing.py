from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    AiguillePosition,
    Coil,
    Position,
)
from domain.train_state import Train
from infrastructure.aiguille.aiguille import Aiguille

LOOP_DELAY_S = 0.05


def set_aiguillage_for_train_passage(
    arduino: ArduinoModbusBridge, train: Train, aiguillage: Aiguille
) -> None:

    if (
        train.objective_position == Position.DIRECT
        or train.objective_position == Position.TALON
    ) and aiguillage.position != AiguillePosition.DIRECT:
        arduino.client.write_coil(
            Coil.BLADE_ORDER.value,
            AiguillePosition.DIRECT.value == 1,
            device_id=arduino.id,
        )
        sleep(LOOP_DELAY_S)

    elif (
        train.objective_position == Position.DEVIEE
        and aiguillage.position != AiguillePosition.DEVIEE
    ):
        arduino.client.write_coil(
            Coil.BLADE_ORDER.value,
            AiguillePosition.DEVIEE.value == 1,
            device_id=arduino.id,
        )
        sleep(LOOP_DELAY_S)
