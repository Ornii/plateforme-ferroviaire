from smbus2 import SMBus


class ArduinoI2cBridge:
    def __init__(self, addr: int):
        self.bus = SMBus(1)
        self.addr = addr
