from pymodbus.client import ModbusSerialClient


class ArduinoModbusBridge:
    def __init__(self, id: int) -> None:
        self.client = ModbusSerialClient(
            port="/dev/ttyUSB0",
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
        )
        self.client.connect()
        self.id = id
