from pymodbus.client import ModbusSerialClient

MODBUS_ID = 0x08
MODBUS_PORT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"


class ArduinoModbusBridge:
    def __init__(self, id: int = MODBUS_ID, port: str = MODBUS_PORT) -> None:
        self.client = ModbusSerialClient(
            port=port,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
        )
        self.client.connect()
        self.id = id
