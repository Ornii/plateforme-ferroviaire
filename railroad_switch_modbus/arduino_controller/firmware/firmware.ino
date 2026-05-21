#include <Servo.h>
#include <ArduinoModbus.h>

// ---------- Protocole Modbus (coils) ----------
// 0: Signal TALON (1=GREEN, 0=RED)
// 1: Signal DIRECT (1=GREEN, 0=RED)
// 2: Signal DEVIEE (1=GREEN, 0=RED)
// 3: Aiguille (1=DIRECT, 0=DEVIEE)
// 4: Hall TALON (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 5: Hall DIRECT (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 6: Hall DEVIEE (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)

enum class TurnoutPosition : uint8_t {
  DIRECT = 1,
  DEVIEE = 0,
};

enum class HallDetection : uint8_t {
  TRAIN_NOT_DETECTED = 0,
  TRAIN_WAS_DETECTED = 1,
};

const int GREEN_LED_TALON_PIN = 2;
const int RED_LED_TALON_PIN = 3;
const int HALL_SENSOR_TALON_PIN = 4;

const int GREEN_LED_DIRECT_PIN = 5;
const int RED_LED_DIRECT_PIN = 6;
const int HALL_SENSOR_DIRECT_PIN = 7;

const int GREEN_LED_DEVIEE_PIN = 8;
const int RED_LED_DEVIEE_PIN = 9;
const int HALL_SENSOR_DEVIEE_PIN = 10;

const int TENSION_TURNOUT_PIN = A0;
const int SERVO_TURNOUT_PIN = 11;
const int TENSION_TURNOUT_THRESHOLD = 700;
const int TURNOUT_SERVO_DIRECT_ANGLE = 15;
const int TURNOUT_SERVO_DEVIEE_ANGLE = 30;

const uint8_t MODBUS_ID = 0x08;
const unsigned long BAUDRATE = 9600;
const int LOOP_DELAY_MS = 50;

constexpr uint16_t COIL_SIGNAL_TALON = 0;
constexpr uint16_t COIL_SIGNAL_DIRECT = 1;
constexpr uint16_t COIL_SIGNAL_DEVIEE = 2;
constexpr uint16_t COIL_BLADE = 3;
constexpr uint16_t COIL_HALL_TALON = 4;
constexpr uint16_t COIL_HALL_DIRECT = 5;
constexpr uint16_t COIL_HALL_DEVIEE = 6;

Servo servo_turnout;
ModbusRTUClient modbus;
TurnoutPosition turnout_position = TurnoutPosition::DIRECT;

void applySignalFromCoil() {

  bool green = modbus.coilRead(MODBUS_ID, COIL_SIGNAL_DIRECT);
  digitalWrite(GREEN_LED_DIRECT_PIN, green);
  digitalWrite(GREEN_LED_DIRECT_PIN, !green);

  bool green = modbus.coilRead(MODBUS_ID, COIL_SIGNAL_DEVIEE);
  digitalWrite(GREEN_LED_DEVIEE_PIN, green);
  digitalWrite(GREEN_LED_DEVIEE_PIN, !green);

  bool green = modbus.coilRead(MODBUS_ID, COIL_SIGNAL_TALON);
  digitalWrite(GREEN_LED_TALON_PIN, green);
  digitalWrite(GREEN_LED_TALON_PIN, !green);


}

void applyTurnoutFromCoil() {
  TurnoutPosition demanded = static_cast<TurnoutPosition>(modbus.coilRead(MODBUS_ID, COIL_BLADE));
  if (demanded != turnout_position) {
    if (demanded == TurnoutPosition::DIRECT) {
      servo_turnout.write(TURNOUT_SERVO_DIRECT_ANGLE);
    } else {
      servo_turnout.write(TURNOUT_SERVO_DEVIEE_ANGLE);
    }
    turnout_position = demanded;
  }
}

void refreshTurnoutPosition() {
    tension_turnout = analogRead(TENSION_TURNOUT_PIN);

    if (tension_turnout >= TENSION_TURNOUT_THRESHOLD) {
        turnout_position = TurnoutPosition::NORMAL;

    } else {
        turnout_position = TurnoutPosition::REVERSE;
    }
    modbus.coilWrite(COIL_BLADE, turnout_position == TurnoutPosition::DIRECT);
}

void refreshHallSensors() {
  HallDetection talon = static_cast<HallDetection>(digitalRead(HALL_SENSOR_TALON_PIN) ^ 1);
  HallDetection direct = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DIRECT_PIN) ^ 1);
  HallDetection deviee = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DEVIEE_PIN) ^ 1);

  if (talon == HallDetection::TRAIN_WAS_DETECTED) modbus.coilWrite(MODBUS_ID, COIL_HALL_TALON, true);
  if (direct == HallDetection::TRAIN_WAS_DETECTED) modbus.coilWrite(MODBUS_ID, COIL_HALL_DIRECT, true);
  if (deviee == HallDetection::TRAIN_WAS_DETECTED) modbus.coilWrite(MODBUS_ID, COIL_HALL_DEVIEE, true);
}

void setup() {
  pinMode(GREEN_LED_TALON_PIN, OUTPUT);
  pinMode(RED_LED_TALON_PIN, OUTPUT);
  pinMode(HALL_SENSOR_TALON_PIN, INPUT);

  pinMode(GREEN_LED_DIRECT_PIN, OUTPUT);
  pinMode(RED_LED_DIRECT_PIN, OUTPUT);
  pinMode(HALL_SENSOR_DIRECT_PIN, INPUT);

  pinMode(GREEN_LED_DEVIEE_PIN, OUTPUT);
  pinMode(RED_LED_DEVIEE_PIN, OUTPUT);
  pinMode(HALL_SENSOR_DEVIEE_PIN, INPUT);

  servo_turnout.attach(SERVO_TURNOUT_PIN);
  Serial.begin(BAUDRATE);

  if (!modbusTCPServer.begin()) {
      Serial.println("Failed to start Modbus TCP Server!");
      while (true) {
        delay(1);
      }
    }

  modbus.configureHoldingRegisters(COIL_SIGNAL_TALON, 1);
  modbus.configureHoldingRegisters(COIL_SIGNAL_DIRECT, 1);
  modbus.configureHoldingRegisters(COIL_SIGNAL_DEVIEE, 1);
  modbus.configureHoldingRegisters(COIL_BLADE, 1);
  modbus.configureHoldingRegisters(COIL_HALL_TALON, 1);
  modbus.configureHoldingRegisters(COIL_HALL_DIRECT, 1);
  modbus.configureHoldingRegisters(COIL_HALL_DEVIEE, 1);

  refreshTurnoutPosition();
}

void loop() {
  int packetReceived = ModbusRTUServer.poll();

  if(packetReceived) {
      applySignalFromCoil();
      applyTurnoutFromCoil();
  }

  refreshTurnoutPosition();
  refreshHallSensors();

  delay(LOOP_DELAY_MS);
