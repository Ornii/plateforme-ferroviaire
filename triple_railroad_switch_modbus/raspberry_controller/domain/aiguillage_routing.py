from time import sleep

from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.packet_protocol import (
    AiguilleState,
    Coil,
    Position,
)
from domain.train_state import Train
from infrastructure.aiguille.aiguille import Aiguille

LOOP_DELAY_S = 0.05


def set_aiguilles_for_train_passage(
    arduino: ArduinoModbusBridge,
    train: Train,
    aiguille_1: Aiguille,
    aiguille_2: Aiguille,
) -> None:

    if (
        train.objective_position == Position.DIRECT
        or train.objective_position == Position.TALON
    ):
        if aiguille_1.state != AiguilleState.GAUCHE:
            arduino.client.write_coil(
                Coil.BLADE_1_ORDER.value,
                bool(AiguilleState.GAUCHE.value),
                device_id=arduino.id,
            )
            sleep(LOOP_DELAY_S)

        if aiguille_2.state != AiguilleState.DROITE:
            arduino.client.write_coil(
                Coil.BLADE_2_ORDER.value,
                bool(AiguilleState.DROITE.value),
                device_id=arduino.id,
            )
            sleep(LOOP_DELAY_S)

    elif train.objective_position == Position.GAUCHE:
        if aiguille_1.state != AiguilleState.GAUCHE:
            arduino.client.write_coil(
                Coil.BLADE_1_ORDER.value,
                bool(AiguilleState.GAUCHE.value),
                device_id=arduino.id,
            )
            sleep(LOOP_DELAY_S)

        if aiguille_2.state != AiguilleState.GAUCHE:
            arduino.client.write_coil(
                Coil.BLADE_2_ORDER.value,
                bool(AiguilleState.GAUCHE.value),
                device_id=arduino.id,
            )
            sleep(LOOP_DELAY_S)

    elif train.objective_position == Position.DROITE:
        if aiguille_1.state != AiguilleState.DROITE:
            arduino.client.write_coil(
                Coil.BLADE_1_ORDER.value,
                bool(AiguilleState.GAUCHE.value),
                device_id=arduino.id,
            )
            sleep(LOOP_DELAY_S)
