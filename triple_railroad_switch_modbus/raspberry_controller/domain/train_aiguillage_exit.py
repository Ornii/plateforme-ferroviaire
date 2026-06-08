from communication.arduino_modbus_bridge import ArduinoModbusBridge
from domain.aiguillage_controller import JunctionState
from domain.packet_protocol import HallDetection
from domain.train_state import TrainState
from infrastructure.signals.signals import set_all_signals_green


def handle_train_exit_detection(
    arduino: ArduinoModbusBridge,
    train: TrainState,
    aiguillage: JunctionState,
) -> None:
    for sensor in aiguillage.hall_sensors.values():
        if (
            sensor.state == HallDetection.TRAIN_WAS_DETECTED
            and sensor.position != train.init_position
        ):
            if sensor.position == train.objective_position:
                train.position = train.objective_position
                set_all_signals_green(arduino, aiguillage.signals)
            else:
                raise ValueError(
                    "Train is not in its objective_position. Issue with aiguillage position."
                )
