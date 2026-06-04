from time import sleep

from pymodbus.client import ModbusSerialClient

MODBUS_ID = 0x08
MODBUS_PORT = "/dev/ttyUSB0"
SIGNAL_COIL = 0
DELAY = 1

client = ModbusSerialClient(
    port=MODBUS_PORT,
    baudrate=9600,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=1,
)

if not client.connect():
    raise ConnectionError(
        f"Unable to connect to Arduino Modbus device {MODBUS_ID} on {MODBUS_PORT}"
    )

try:
    client.write_coil(SIGNAL_COIL, True, device_id=MODBUS_ID)
    sleep(DELAY)
    result = client.read_coils(SIGNAL_COIL, count=1, device_id=MODBUS_ID).bits[0]
    print(f"The result is {result}")
    sleep(DELAY)
    client.write_coil(SIGNAL_COIL, False, device_id=MODBUS_ID)
    sleep(DELAY)
finally:
    client.close()
