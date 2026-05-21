#include <Servo.h>
#include <Wire.h>

enum class Function : uint8_t {
    SET_TRAFFIC_LIGHTS = 0b000,
    SET_TURNOUT = 0b001,
    GET_TURNOUT = 0b010,
    SEND_TURNOUT = 0b011,
    GET_HALL_SENSORS = 0b100,
    SEND_HALL_SENSORS = 0b101,
    RESET_HALL_SENSORS = 0b110
};

enum class Position : uint8_t {
    TALON = 0b00,
    DIRECT = 0b01,
    DEVIEE = 0b10,
    FROG = 0b11
};

enum class SignalColor : uint8_t {
    RED = 0b00,
    YELLOW = 0b10,
    GREEN = 0b11
};

enum class TurnoutPosition : uint8_t {
    DIRECT = 0b1,
    DEVIEE = 0b0
};

enum class HallDetection : uint8_t {
    TRAIN_NOT_DETECTED = 0b0,
    TRAIN_WAS_DETECTED = 0b1
};


// Lead Position
const int GREEN_LED_TALON_PIN = 2;
const int RED_LED_TALON_PIN = 3;
const int HALL_SENSOR_TALON_PIN = 4;
HallDetection hall_sensor_lead_state = HallDetection::TRAIN_NOT_DETECTED;

// Normal Position
const int GREEN_LED_DIRECT_PIN = 5;
const int RED_LED_DIRECT_PIN = 6;
const int HALL_SENSOR_DIRECT_PIN = 7;
HallDetection hall_sensor_normal_state = HallDetection::TRAIN_NOT_DETECTED;

// Reverse Position
const int GREEN_LED_DEVIEE_PIN = 8;
const int RED_LED_DEVIEE_PIN = 9;
const int HALL_SENSOR_DEVIEE_PIN = 10;
HallDetection hall_sensor_reverse_state = HallDetection::TRAIN_NOT_DETECTED;


// Frog Position
const int TENSION_TURNOUT_PIN = A0;
const int SERVO_TURNOUT_PIN = 11;
const int TENSION_TURNOUT_THRESHOLD = 700;
const int TURNOUT_SERVO_DIRECT_ANGLE = 15;
const int TURNOUT_SERVO_DEVIEE_ANGLE = 30;
Servo servo_turnout;
int tension_turnout;
TurnoutPosition turnout_position = TurnoutPosition::DIRECT; // Temporary value


// Constants
const int LOOP_DELAY_MS = 50;
const uint8_t MODBUS_ADDRESS = 0x08;


// Packet modified before each response when the master requests a value
uint8_t packet_to_send = 0;


HallDetection hall_sensors_state[3] = {
    HallDetection::TRAIN_NOT_DETECTED, // Lead Position
    HallDetection::TRAIN_NOT_DETECTED, // Normal Position
    HallDetection::TRAIN_NOT_DETECTED  // Reverse Position
};


void setup() {
    // Modbus
    Wire.begin(MODBUS_ADDRESS);
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    // Lead Position
    pinMode(GREEN_LED_TALON_PIN, OUTPUT);
    pinMode(RED_LED_TALON_PIN, OUTPUT);
    pinMode(HALL_SENSOR_TALON_PIN, INPUT);

    // Normal Position
    pinMode(GREEN_LED_DIRECT_PIN, OUTPUT);
    pinMode(RED_LED_DIRECT_PIN, OUTPUT);
    pinMode(HALL_SENSOR_DIRECT_PIN, INPUT);

    // Reverse Position
    pinMode(GREEN_LED_DEVIEE_PIN, OUTPUT);
    pinMode(RED_LED_DEVIEE_PIN, OUTPUT);
    pinMode(HALL_SENSOR_DEVIEE_PIN, INPUT);

    // Frog Position
    servo_turnout.attach(SERVO_TURNOUT_PIN);
    refreshTurnoutPosition();


}


void setLed(uint8_t packet) {
    Position position = static_cast<Position>((packet >> 5) & 0b11);
    SignalColor color = static_cast<SignalColor>((packet >> 3) & 0b11);

    if (position == Position::TALON){

        digitalWrite(GREEN_LED_TALON_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_TALON_PIN, color == SignalColor::RED);


    } else if (position == Position::DIRECT) {

        digitalWrite(GREEN_LED_DIRECT_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_DIRECT_PIN, color == SignalColor::RED);

    } else if (position == Position::DEVIEE) {


        digitalWrite(GREEN_LED_DEVIEE_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_DEVIEE_PIN, color == SignalColor::RED);

    }
}

void setTurnout(uint8_t packet) {
    TurnoutPosition demand_turnout_position = static_cast<TurnoutPosition>((packet >> 3) & 0b1);

    if (demand_turnout_position != turnout_position) {
        if (demand_turnout_position == TurnoutPosition::DIRECT) {
            servo_turnout.write(TURNOUT_SERVO_DIRECT_ANGLE);
        } else {
                servo_turnout.write(TURNOUT_SERVO_DEVIEE_ANGLE);
            }

    }
    turnout_position = demand_turnout_position;
}


void refreshTurnoutPosition() {
    tension_turnout = analogRead(TENSION_TURNOUT_PIN);

    if (tension_turnout >= TENSION_TURNOUT_THRESHOLD) {
        turnout_position = TurnoutPosition::DIRECT;

    } else {
        turnout_position = TurnoutPosition::DEVIEE;
    }

}

void refreshHallSensors() {
    HallDetection hall_sensor_reverse_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DEVIEE_PIN) ^ 1);
    HallDetection hall_sensor_normal_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_DIRECT_PIN) ^ 1);
    HallDetection hall_sensor_lead_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_TALON_PIN) ^ 1);


    if (hall_sensor_lead_state_new == HallDetection::TRAIN_WAS_DETECTED)  {
            hall_sensor_lead_state = HallDetection::TRAIN_WAS_DETECTED;
        }

    if (hall_sensor_normal_state_new == HallDetection::TRAIN_WAS_DETECTED)  {
            hall_sensor_normal_state = HallDetection::TRAIN_WAS_DETECTED;
        }
    if (hall_sensor_reverse_state_new == HallDetection::TRAIN_WAS_DETECTED)  {
            hall_sensor_reverse_state = HallDetection::TRAIN_WAS_DETECTED;
        }

        hall_sensors_state[0] = hall_sensor_lead_state;
        hall_sensors_state[1] = hall_sensor_normal_state;
        hall_sensors_state[2] = hall_sensor_reverse_state;
}


void sendHallSensors() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | static_cast<uint8_t>(Function::SEND_HALL_SENSORS);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[0]) << 5);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[1]) << 4);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[2]) << 3);
}

void sendTurnout() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | static_cast<uint8_t>(Function::SEND_TURNOUT);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(turnout_position) << 3);
}


void resetHallSensors() {
    hall_sensor_lead_state = HallDetection::TRAIN_NOT_DETECTED;
    hall_sensor_normal_state = HallDetection::TRAIN_NOT_DETECTED;
    hall_sensor_reverse_state = HallDetection::TRAIN_NOT_DETECTED;
    hall_sensors_state[0] = HallDetection::TRAIN_NOT_DETECTED;
    hall_sensors_state[1] = HallDetection::TRAIN_NOT_DETECTED;
    hall_sensors_state[2] = HallDetection::TRAIN_NOT_DETECTED;
}


void requestEvent() {
    Wire.write(packet_to_send);
}

void receiveEvent(int howMany) {
    if (Wire.available()) {
        uint8_t packet = Wire.read();

    Function function = static_cast<Function>(packet & 0b111);

    if (function == Function::SET_TRAFFIC_LIGHTS) {
        setLed(packet);
    } else if (function == Function::SET_TURNOUT) {
        setTurnout(packet);
    } else if (function == Function::GET_TURNOUT) {
        sendTurnout();
    } else if (function == Function::GET_HALL_SENSORS) {
        sendHallSensors();
    } else if (function == Function::RESET_HALL_SENSORS) {
        resetHallSensors();
    }
    }
}

void loop() {
    delay(LOOP_DELAY_MS);
    refreshTurnoutPosition();
    refreshHallSensors();
}
