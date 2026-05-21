from pymodbus.client import ModbusSerialClient


MODBUS_ID = 0x08


class ArduinoModbusBridge:
    def __init__(self, id: int = MODBUS_ID) -> None:
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
