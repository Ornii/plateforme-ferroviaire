#include <Servo.h>
#include <Wire.h>

enum class Function : uint8_t {
    SET_LED = 0b000,
    SET_TURNOUT = 0b001,
    GET_HALL_SENSORS = 0b010,
    GET_TURNOUT = 0b011?
    RESET_HALL_SENSORS = 0b100
};

enum class Position : uint8_t {
    LEAD = 0b00,
    NORMAL = 0b01,
    REVERSE = 0b10,
    FROG = 0b11
};

enum class SignalColor : uint8_t {
    RED = 0b00,
    YELLOW = 0b10,
    GREEN = 0b11
};

enum class TurnoutPosition : uint8_t {
    NORMAL = 0b1,
    REVERSE = 0b0
};

enum class HallDetection : uint8_t {
    TRAIN_NOT_DETECTED = 0b0,
    TRAIN_WAS_DETECTED = 0b1
};


// Lead Position
const int GREEN_LED_LEAD_PIN = 2;
const int RED_LED_LEAD_PIN = 3;
const int HALL_SENSOR_LEAD_PIN = 4;
HallDetection hall_sensor_lead_state = HallDetection::TRAIN_NOT_DETECTED;

// Normal Position
const int GREEN_LED_NORMAL_PIN = 5;
const int RED_LED_NORMAL_PIN = 6;
const int HALL_SENSOR_NORMAL_PIN = 7;
HallDetection hall_sensor_normal_state = HallDetection::TRAIN_NOT_DETECTED;

// Reverse Position
const int GREEN_LED_REVERSE_PIN = 8;
const int RED_LED_REVERSE_PIN = 9;
const int HALL_SENSOR_REVERSE_PIN = 10;
HallDetection hall_sensor_reverse_state = HallDetection::TRAIN_NOT_DETECTED;


// Frog Position
const int TENSION_TURNOUT_PIN = A0;
const int SERVO_TURNOUT_PIN = 11;
const int TENSION_TURNOUT_THRESHOLD = 700;
const int TURNOUT_SERVO_NORMAL_ANGLE = 15;
const int TURNOUT_SERVO_REVERSE_ANGLE = 30;
Servo servo_turnout;
int tension_turnout;
TurnoutPosition turnout_position = TurnoutPosition::NORMAL; // Temporary value


// Constants
const int LOOP_DELAY_MS = 250;
const uint8_t I2C_ADDRESS = 0x08;


// Packet modified before each response when the master requests a value
uint8_t packet_to_send = 0;


// TODO: reset hall_sensors_state when train arrived
HallDetection hall_sensors_state[3] = {
    HallDetection::TRAIN_NOT_DETECTED, // Lead Position
    HallDetection::TRAIN_NOT_DETECTED, // Normal Position
    HallDetection::TRAIN_NOT_DETECTED  // Reverse Position
};


void setup() {
    // I2C
    Wire.begin(I2C_ADDRESS);
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    // Lead Position
    pinMode(GREEN_LED_LEAD_PIN, OUTPUT);
    pinMode(RED_LED_LEAD_PIN, OUTPUT);
    pinMode(HALL_SENSOR_LEAD_PIN, INPUT);

    // Normal Position
    pinMode(GREEN_LED_NORMAL_PIN, OUTPUT);
    pinMode(RED_LED_NORMAL_PIN, OUTPUT);
    pinMode(HALL_SENSOR_NORMAL_PIN, INPUT);

    // Reverse Position
    pinMode(GREEN_LED_REVERSE_PIN, OUTPUT);
    pinMode(RED_LED_REVERSE_PIN, OUTPUT);
    pinMode(HALL_SENSOR_REVERSE_PIN, INPUT);

    // Frog Position
    servo_turnout.attach(SERVO_TURNOUT_PIN);
    refreshTurnoutPosition();

}


void setLed(uint8_t packet) {
    Position position = static_cast<Position>((packet >> 5) & 0b11);
    SignalColor color = static_cast<SignalColor>((packet >> 3) & 0b11);

    if (position == Position::LEAD){

        digitalWrite(GREEN_LED_LEAD_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_LEAD_PIN, color == SignalColor::RED);


    } else if (position == Position::NORMAL) {

        digitalWrite(GREEN_LED_NORMAL_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_NORMAL_PIN, color == SignalColor::RED);

    } else if (position == Position::REVERSE) {


        digitalWrite(GREEN_LED_REVERSE_PIN, color == SignalColor::GREEN);
        digitalWrite(RED_LED_REVERSE_PIN, color == SignalColor::RED);

    }
}

void setTurnout(uint8_t packet) {
    TurnoutPosition demand_turnout_position = static_cast<TurnoutPosition>((packet >> 3) & 0b1);

    if (demand_turnout_position != turnout_position) {
        if (demand_turnout_position == TurnoutPosition::NORMAL) {
            servo_turnout.write(TURNOUT_SERVO_NORMAL_ANGLE);
        } else {
                servo_turnout.write(TURNOUT_SERVO_REVERSE_ANGLE);
            }

    }
    turnout_position = demand_turnout_position;
}


void refreshTurnoutPosition() {
    tension_turnout = analogRead(TENSION_TURNOUT_PIN);

    if (tension_turnout >= TENSION_TURNOUT_THRESHOLD) {
        turnout_position = TurnoutPosition::NORMAL;

    } else {
        turnout_position = TurnoutPosition::REVERSE;
    }

}

void refreshHallSensors() {
    HallDetection hall_sensor_reverse_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_REVERSE_PIN) ^ 1);
    HallDetection hall_sensor_normal_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_NORMAL_PIN) ^ 1);
    HallDetection hall_sensor_lead_state_new = static_cast<HallDetection>(digitalRead(HALL_SENSOR_LEAD_PIN) ^ 1);


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
    packet_to_send = packet_to_send | (static_cast<uint8_t>(Function::GET_HALL_SENSORS) <<  1);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[0]) << 5);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[1]) << 4);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(hall_sensors_state[2]) << 3);
}

void sendTurnout() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | (static_cast<uint8_t>(Function::GET_TURNOUT) <<  1);
    packet_to_send = packet_to_send | (static_cast<uint8_t>(turnout_position) << 3);
}


void resetHallSensors() {
    hall_sensors_state[3] = {
        HallDetection::TRAIN_NOT_DETECTED, // Lead Position
        HallDetection::TRAIN_NOT_DETECTED, // Normal Position
        HallDetection::TRAIN_NOT_DETECTED  // Reverse Position
    };
}


void requestEvent() {
    Wire.write(packet_to_send);
}

void receiveEvent(int howMany) {
    if (Wire.available()) {
        uint8_t packet = Wire.read();

    Function function = static_cast<Function>(packet & 0b111);

    if (function == Function::SET_LED) {
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
    delay(LOOP_DELAY_MS);  // Avoid spamming
    refreshTurnoutPosition();
    refreshHallSensors();
}
