#include <Servo.h>
#include <ArduinoRS485.h>
#include <ArduinoModbus.h>

// ---------- Protocole Modbus (coils) ----------
// 0: Signal TALON (1=GREEN, 0=RED)
// 1: Signal DIRECT (1=GREEN, 0=RED)
// 2: Signal GAUCHE (1=GREEN, 0=RED)
// 3: Signal DROITE (1=GREEN, 0=RED)
// 4: Hall TALON (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 5: Hall DIRECT (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 6: Hall GAUCHE (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 7: Hall DROITE (1=TRAIN_WAS_DETECTED, 0=TRAIN_NOT_DETECTED)
// 8: Aiguille 1 order (1=DIRECT, 0=GAUCHE) (Aiguille 1 is the nearest of the talon position)
// 9: Aiguille 1 feedback (1=DIRECT, 0=GAUCHE)
// 10: Aiguille 2 order (1=DIRECT, 0=GAUCHE)
// 11: Aiguille 2 feedback (1=DIRECT, 0=GAUCHE)

constexpr uint16_t COIL_SIGNAL_TALON = 0;
constexpr uint16_t COIL_SIGNAL_DIRECT = 1;
constexpr uint16_t COIL_SIGNAL_GAUCHE = 2;
constexpr uint16_t COIL_SIGNAL_DROITE = 3;
constexpr uint16_t COIL_HALL_TALON = 4;
constexpr uint16_t COIL_HALL_DIRECT = 5;
constexpr uint16_t COIL_HALL_GAUCHE = 6;
constexpr uint16_t COIL_HALL_DROITE = 7;
constexpr uint16_t COIL_BLADE_1_ORDER = 8;
constexpr uint16_t COIL_BLADE_1_FEEDBACK = 9;
constexpr uint16_t COIL_BLADE_2_ORDER = 10;
constexpr uint16_t COIL_BLADE_2_FEEDBACK = 11;

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

const int GREEN_LED_GAUCHE_PIN = 8;
const int RED_LED_GAUCHE_PIN = 9;
const int HALL_SENSOR_GAUCHE_PIN = 10;

const int GREEN_LED_DROITE_PIN = 11;
const int RED_LED_DROITE_PIN = 12;
const int HALL_SENSOR_DROITE_PIN = 13;

const int TENSION_TURNOUT_1_PIN = A0;
const int TENSION_TURNOUT_2_PIN = A1;
const int SERVO_1_TURNOUT_PIN = 14;
const int SERVO_2_TURNOUT_PIN = 15;
const int TENSION_TURNOUT_THRESHOLD = 700;
const int TURNOUT_SERVO_DIRECT_ANGLE = 30;
const int TURNOUT_SERVO_DEVIEE_ANGLE = 60;

const uint8_t MODBUS_ID = 0x08;
const unsigned long BAUDRATE = 9600;
const int LOOP_DELAY_MS = 50;
const int TX_PIN = 1;
const int RE_DE_PIN = 16;


Servo servo_1_turnout;
Servo servo_2_turnout;

TurnoutPosition turnout_1_position = TurnoutPosition::DIRECT;
TurnoutPosition turnout_2_position = TurnoutPosition::DIRECT;

int tension_turnout_1 = 0;
int tension_turnout_2 = 0;


void applySignalsFromCoils() {
  bool greenDirect = ModbusRTUServer.coilRead(COIL_SIGNAL_DIRECT);
  digitalWrite(GREEN_LED_DIRECT_PIN, greenDirect);
  digitalWrite(RED_LED_DIRECT_PIN, !greenDirect);

  bool greenGauche = ModbusRTUServer.coilRead(COIL_SIGNAL_GAUCHE);
  digitalWrite(GREEN_LED_GAUCHE_PIN, greenGauche);
  digitalWrite(RED_LED_GAUCHE_PIN, !greenGauche);

  bool greenDroite = ModbusRTUServer.coilRead(COIL_SIGNAL_DROITE);
  digitalWrite(GREEN_LED_DROITE_PIN, greenDroite);
  digitalWrite(RED_LED_DROITE_PIN, !greenDroite);

  bool greenTalon = ModbusRTUServer.coilRead(COIL_SIGNAL_TALON);
  digitalWrite(GREEN_LED_TALON_PIN, greenTalon);
  digitalWrite(RED_LED_TALON_PIN, !greenTalon);
}

void applyTurnoutFromCoil() {
  TurnoutPosition demanded_blade_1 = static_cast<TurnoutPosition>(ModbusRTUServer.coilRead(COIL_BLADE_1_ORDER));

  if (demanded_blade_1 != turnout_1_position) {
    if (demanded_blade_1 == TurnoutPosition::DIRECT) {
      servo_1_turnout.write(TURNOUT_SERVO_DIRECT_ANGLE);
    } else {
      servo_1_turnout.write(TURNOUT_SERVO_DEVIEE_ANGLE);
    }
    turnout_1_position = demanded_blade_1;
  }

  TurnoutPosition demanded_blade_2 = static_cast<TurnoutPosition>(ModbusRTUServer.coilRead(COIL_BLADE_2_ORDER));

  if (demanded_blade_2 != turnout_2_position) {
    if (demanded_blade_2 == TurnoutPosition::DIRECT) {
      servo_2_turnout.write(TURNOUT_SERVO_DIRECT_ANGLE);
    } else {
      servo_2_turnout.write(TURNOUT_SERVO_DEVIEE_ANGLE);
    }
    turnout_2_position = demanded_blade_2;
  }
}

void refreshTurnoutPosition() {
  tension_turnout_1 = analogRead(TENSION_TURNOUT_1_PIN);

  if (tension_turnout_1 >= TENSION_TURNOUT_THRESHOLD) {
    turnout_1_position = TurnoutPosition::DIRECT;
  } else {
    turnout_1_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_1_FEEDBACK, turnout_1_position == TurnoutPosition::DIRECT);

  tension_turnout_2 = analogRead(TENSION_TURNOUT_2_PIN);

  if (tension_turnout_2 >= TENSION_TURNOUT_THRESHOLD) {
    turnout_2_position = TurnoutPosition::DIRECT;
  } else {
    turnout_2_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_2_FEEDBACK, turnout_2_position == TurnoutPosition::DIRECT);

}

// Raspberry sets state TRAIN_NOT_DETECTED manually
void refreshHallSensors() {
  HallDetection hall_sensor_talon_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_TALON_PIN) ^ 1);
  HallDetection hall_sensor_direct_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DIRECT_PIN) ^ 1);
  HallDetection hall_sensor_gauche_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_GAUCHE_PIN) ^ 1);
  HallDetection hall_sensor_droite_state = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DROITE_PIN) ^ 1);

  if (hall_sensor_talon_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_TALON, true);
  }
  if (hall_sensor_direct_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_DIRECT, true);
  }
  if (hall_sensor_gauche_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_GAUCHE, true);
  }
  if (hall_sensor_droite_state == HallDetection::TRAIN_WAS_DETECTED) {
      ModbusRTUServer.coilWrite(COIL_HALL_DROITE, true);
  }
}

void setup() {
  pinMode(GREEN_LED_TALON_PIN, OUTPUT);
  pinMode(RED_LED_TALON_PIN, OUTPUT);
  pinMode(HALL_SENSOR_TALON_PIN, INPUT);

  pinMode(GREEN_LED_DIRECT_PIN, OUTPUT);
  pinMode(RED_LED_DIRECT_PIN, OUTPUT);
  pinMode(HALL_SENSOR_DIRECT_PIN, INPUT);

  pinMode(GREEN_LED_GAUCHE_PIN, OUTPUT);
  pinMode(RED_LED_GAUCHE_PIN, OUTPUT);
  pinMode(HALL_SENSOR_GAUCHE_PIN, INPUT);

  pinMode(GREEN_LED_DROITE_PIN, OUTPUT);
  pinMode(RED_LED_DROITE_PIN, OUTPUT);
  pinMode(HALL_SENSOR_DROITE_PIN, INPUT);

  servo_1_turnout.attach(SERVO_1_TURNOUT_PIN);
  servo_2_turnout.attach(SERVO_2_TURNOUT_PIN);

  RS485.setPins(TX_PIN, RE_DE_PIN, RE_DE_PIN);
  if (!ModbusRTUServer.begin(MODBUS_ID, BAUDRATE)) {
    while (true) {
      delay(1);
    }
  }

  ModbusRTUServer.configureCoils(0, 14);

  ModbusRTUServer.coilWrite(COIL_SIGNAL_TALON, false);
  ModbusRTUServer.coilWrite(COIL_SIGNAL_DIRECT, false);
  ModbusRTUServer.coilWrite(COIL_SIGNAL_GAUCHE, false);
  ModbusRTUServer.coilWrite(COIL_SIGNAL_DROITE, false);
  ModbusRTUServer.coilWrite(COIL_HALL_TALON, false);
  ModbusRTUServer.coilWrite(COIL_HALL_DIRECT, false);
  ModbusRTUServer.coilWrite(COIL_HALL_GAUCHE, false);
  ModbusRTUServer.coilWrite(COIL_HALL_DROITE, false);

  tension_turnout_1 = analogRead(TENSION_TURNOUT_1_PIN);

  if (tension_turnout_1 >= TENSION_TURNOUT_THRESHOLD) {
      turnout_1_position = TurnoutPosition::DIRECT;
  } else {
      turnout_1_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_1_ORDER, turnout_1_position == TurnoutPosition::DIRECT); // order at this point could be not given
  ModbusRTUServer.coilWrite(COIL_BLADE_1_FEEDBACK, turnout_1_position == TurnoutPosition::DIRECT);

  tension_turnout_2 = analogRead(TENSION_TURNOUT_2_PIN);

  if (tension_turnout_2 >= TENSION_TURNOUT_THRESHOLD) {
      turnout_2_position = TurnoutPosition::DIRECT;
  } else {
      turnout_2_position = TurnoutPosition::DEVIEE;
  }

  ModbusRTUServer.coilWrite(COIL_BLADE_2_ORDER, turnout_2_position == TurnoutPosition::DIRECT); // order at this point could be not given
  ModbusRTUServer.coilWrite(COIL_BLADE_2_FEEDBACK, turnout_2_position == TurnoutPosition::DIRECT);
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
