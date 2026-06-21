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
        train.objective_position == Position.ID_1
        or train.objective_position == Position.ID_4
    ) and aiguillage.position != AiguillePosition.DROITE:
        arduino.client.write_coil(
            Coil.BLADE_ORDER.value,
            bool(AiguillePosition.DROITE.value),
            device_id=arduino.id,
        )
        sleep(LOOP_DELAY_S)

    elif (
        train.objective_position == Position.ID_2
        or train.objective_position == Position.ID_3
    ) and aiguillage.position != AiguillePosition.GAUCHE:
        arduino.client.write_coil(
            Coil.BLADE_ORDER.value,
            bool(AiguillePosition.GAUCHE.value),
            device_id=arduino.id,
        )
        sleep(LOOP_DELAY_S)
