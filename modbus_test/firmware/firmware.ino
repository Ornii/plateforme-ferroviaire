#include <ArduinoRS485.h>
#include <ArduinoModbus.h>

const int GREEN_LED_PIN = 2;
const int TX_PIN = 1;
const int RE_DE_pin = 13;
constexpr uint16_t COIL_SIGNAL = 0;
const uint8_t MODBUS_ID = 0x08;
const unsigned long BAUDRATE = 9600;
const int LOOP_DELAY_MS = 50;

void setup() {
  pinMode(GREEN_LED_PIN, OUTPUT);
  RS485.setPins(TX_PIN, RE_DE_pin, RE_DE_pin);

  if (!ModbusRTUServer.begin(MODBUS_ID, BAUDRATE)) {
    while (true) {
        delay(1);
    }
  }

  ModbusRTUServer.configureCoils(0, 1);
}

void loop() {
  if (ModbusRTUServer.poll()) {
      bool green = ModbusRTUServer.coilRead(COIL_SIGNAL);
      digitalWrite(GREEN_LED_PIN, green);
  }

  delay(LOOP_DELAY_MS);
}
