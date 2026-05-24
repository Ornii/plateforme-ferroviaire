#include <Servo.h>
#include <ArduinoRS485.h>
#include <ArduinoModbus.h>

// ---------- Protocole Modbus (coils) ----------
// 0: Signal TALON (1=GREEN, 0=RED)
// 1: Signal DIRECT (1=GREEN, 0=RED)
// 2: Signal DEVIEE (1=GREEN, 0=RED)
// 3: Hall TALON (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 4: Hall DIRECT (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 5: Hall DEVIEE (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 6: Aiguille order (1=DIRECT, 0=DEVIEE)
// 7: Aiguille feedback (1=DIRECT, 0=DEVIEE)

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
constexpr uint16_t COIL_HALL_TALON = 3;
constexpr uint16_t COIL_HALL_DIRECT = 4;
constexpr uint16_t COIL_HALL_DEVIEE = 5;
constexpr uint16_t COIL_BLADE_ORDER = 6;
constexpr uint16_t COIL_BLADE_FEEDBACK = 7;

Servo servo_turnout;
TurnoutPosition turnout_position = TurnoutPosition::DIRECT;
int tension_turnout = 0;


void applySignalsFromCoils() {
  bool greenDirect = ModbusRTUServer.coilRead(COIL_SIGNAL_DIRECT);
  digitalWrite(GREEN_LED_DIRECT_PIN, greenDirect);
  digitalWrite(RED_LED_DIRECT_PIN, !greenDirect);

  bool greenDeviee = ModbusRTUServer.coilRead(COIL_SIGNAL_DEVIEE);
  digitalWrite(GREEN_LED_DEVIEE_PIN, greenDeviee);
  digitalWrite(RED_LED_DEVIEE_PIN, !greenDeviee);

  bool greenTalon = ModbusRTUServer.coilRead(COIL_SIGNAL_TALON);
  digitalWrite(GREEN_LED_TALON_PIN, greenTalon);
  digitalWrite(RED_LED_TALON_PIN, !greenTalon);
}

void applyTurnoutFromCoil() {
  TurnoutPosition demanded = static_cast<TurnoutPosition>(ModbusRTUServer.coilRead(COIL_BLADE_ORDER));
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
    turnout_position = TurnoutPosition::DIRECT;
  } else {
    turnout_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_FEEDBACK, turnout_position == TurnoutPosition::DIRECT);
}

// Raspberry sets state TRAIN_NOT_DETECTED manually
void refreshHallSensors() {
  HallDetection hall_sensor_talon_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_TALON_PIN) ^ 1);
  HallDetection hall_sensor_direct_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DIRECT_PIN) ^ 1);
  HallDetection hall_sensor_deviee_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DEVIEE_PIN) ^ 1);

  if (hall_sensor_talon_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_TALON, true);
  }
  if (hall_sensor_direct_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_DIRECT, true);
  }
  if (hall_sensor_deviee_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_DEVIEE, true);
  }
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

  if (!ModbusRTUServer.begin(MODBUS_ID, BAUDRATE)) {
    while (true) {
      delay(1);
    }
  }

  ModbusRTUServer.configureCoils(0, 8);

  ModbusRTUServer.coilWrite(COIL_SIGNAL_TALON, false);
  ModbusRTUServer.coilWrite(COIL_SIGNAL_DIRECT, false);
  ModbusRTUServer.coilWrite(COIL_SIGNAL_DEVIEE, false);
  ModbusRTUServer.coilWrite(COIL_HALL_TALON, false);
  ModbusRTUServer.coilWrite(COIL_HALL_DIRECT, false);
  ModbusRTUServer.coilWrite(COIL_HALL_DEVIEE, false);

  tension_turnout = analogRead(TENSION_TURNOUT_PIN);

  if (tension_turnout >= TENSION_TURNOUT_THRESHOLD) {
      turnout_position = TurnoutPosition::DIRECT;
  } else {
      turnout_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_ORDER, turnout_position == TurnoutPosition::DIRECT); // order at this point is still not given
  ModbusRTUServer.coilWrite(COIL_BLADE_FEEDBACK, turnout_position == TurnoutPosition::DIRECT);

}

void loop() {
  refreshTurnoutPosition();
  refreshHallSensors();

  if (ModbusRTUServer.poll()) {
    applySignalsFromCoils();
    applyTurnoutFromCoil();
  }

  delay(LOOP_DELAY_MS);
}
