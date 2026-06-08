from communication.arduino_i2c_bridge import ArduinoI2cBridge
from domain.junction_controller import JunctionState
from domain.packet_protocol import HallDetection
from domain.train_state import TrainState
from infrastructure.signals.signals import set_all_signals_green


def handle_train_exit_detection(
    arduino: ArduinoI2cBridge,
    train: TrainState,
    junction: JunctionState,
) -> None:
    for sensor in junction.hall_sensors.values():
        if (
            sensor.state == HallDetection.TRAIN_WAS_DETECTED
            and sensor.position != train.init_position
        ):
            if sensor.position == train.objective_position:
                train.position = train.objective_position
                set_all_signals_green(arduino, junction.signals)
            else:
                raise ValueError(
                    "Train is not in its objective_position. Issue with turnout position."
                )
