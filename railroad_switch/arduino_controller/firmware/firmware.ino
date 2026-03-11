#include <Wire.h>
#include <Servo.h>


enum Function {
    SET_LED = 0b00,
    SET_TURNOUT = 0b01,
    GET_HALL_SENSORS = 0b10,
    GET_TURNOUT = 0b11
};

enum Position {
    LEAD = 0b00,
    NORMAL = 0b01,
    REVERSE = 0b10,
    FROG = 0b11
};

enum SignalColor {
    RED = 0b00,
    YELLOW = 0b10,
    GREEN = 0b11
};

enum TurnoutPosition {
    NORMAL = 0b1,
    REVERSE = 0b0
};

enum HallDetection {
    TRAIN_NOT_DETECTED = 0b0,
    TRAIN_WAS_DETECTED = 0b1
};


// Lead Position
const int green_led_lead_pin = 2;
const int red_led_lead_pin = 3;
const int hall_sensor_lead_pin = 4;
HallDetection hall_sensor_lead_state = TRAIN_NOT_DETECTED;

// Normal Position
const int green_led_normal_pin = 5;
const int red_led_normal_pin = 6;
const int hall_sensor_normal_pin = 7;
HallDetection hall_sensor_normal_state = TRAIN_NOT_DETECTED;

// Reverse Position
const int green_led_reverse_pin_pin= 8;
const int red_led_reverse_pin = 9;
const int hall_sensor_reverse_pin = 10;
HallDetection hall_sensor_reverse_state = TRAIN_NOT_DETECTED;


// Frog Position
const int tension_turnout_pin = A0;
const int servo_turnout_pin = 11;
Servo servo_turnout;
int tension_turnout;
TurnoutPosition turnout_position;

int packet_to_send = 0; // packet which is modified each time the client received a "get" order and then send


// TODO: reset to 0 hall_sensors_state when train arrived
uint8_t hall_sensors_state[3] = {
    0, // Lead Position
    0, // Normal Position
    0  // Reverse Position
};


void setup() {
    // I2C 
    Wire.begin(0x08);
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);

    // Lead Position
    pinMode(green_led_lead_pin, OUTPUT);
    pinMode(red_led_lead_pin, OUTPUT);
    pinMode(hall_sensor_lead_pin, INPUT);

    // Normal Position
    pinMode(green_led_normal_pin, OUTPUT);
    pinMode(red_led_normal_pin, OUTPUT);
    pinMode(hall_sensor_normal_pin, INPUT);

    // Reverse Position
    pinMode(green_led_reverse_pin, OUTPUT);
    pinMode(red_led_reverse_pin, OUTPUT);
    pinMode(hall_sensor_reverse_pin, INPUT);

    // Frog Position
    servo_turnout.attach(servo_turnout_pin);
    servo_turnout.write(15);  // initial neutral position
    refreshTurnoutPosition();

}



void receiveEvent(int howMany) {
    while (Wire.available()) {
    int packet = Wire.read();

    Function function = ((packet >> 1) & 0b11);

    if (function == SET_LED) {
        setLed(packet);
    } else if (function == SET_TURNOUT) {
        setTurnout(packet);
    } else if (function == GET_TURNOUT) {
        sendTurnout();
    } else if (function == GET_HALL_SENSORS) {
        sendHallSensors();
    }
    }
}

void setLed(int packet) {
    Position position = ((packet >> 5) & 0b111);
    SignalColor color = ((packet >> 3) & 0b11);

    if (position == LEAD){

        digitalWrite(green_led_lead_pin, color == GREEN);
        digitalWrite(red_led_lead_pin, color == RED);


    } else if (position == NORMAL) {

        digitalWrite(green_led_normal_pin, color == GREEN);
        digitalWrite(red_led_normal_pin, color == RED);

    } else if (position == REVERSE) {


        digitalWrite(green_led_reverse_pin, color == GREEN);
        digitalWrite(red_led_reverse_pin, color == RED);

    }
}

void setTurnout(int packet) {
    TurnoutPosition demand_turnout_position = ((packet >> 3) & 0b1);

    if (!(demand_turnout_position == turnout_position)) {
        if (demand_turnout_position == NORMAL) {
            servo_turnout.write(15);
        } else if (demand_turnout_position == REVERSE){
                servo_turnout.write(30);
            }

    }
    turnout_position = demand_turnout_position;
}

void refreshTurnoutPosition() {
    tension_turnout = analogRead(tension_turnout_pin);

    if (tension_turnout >= 700) {
        turnout_position = NORMAL;

    } else {
        turnout_position = REVERSE;
    }

}

void refreshHallSensors() {
    HallDetection hall_sensor_reverse_state_new = digitalRead(hall_sensor_reverse_pin) ^ 1;
    HallDetection hall_sensor_normal_state_new = digitalRead(hall_sensor_normal_pin) ^ 1;
    HallDetection hall_sensor_lead_state_new = digitalRead(hall_sensor_lead_pin) ^ 1;


    if (hall_sensor_lead_state_new == TRAIN_WAS_DETECTED)  {
            hall_sensor_lead_state = TRAIN_WAS_DETECTED;
        }

    if (hall_sensor_normal_state_new == TRAIN_WAS_DETECTED)  {
            hall_sensor_normal_state = TRAIN_WAS_DETECTED;
        }
    if (hall_sensor_reverse_state_new == TRAIN_WAS_DETECTED)  {
            hall_sensor_reverse_state = TRAIN_WAS_DETECTED;
        }

        hall_sensors_state[0] = hall_sensor_lead_state;
        hall_sensors_state[1] = hall_sensor_normal_state;
        hall_sensors_state[2] = hall_sensor_reverse_state;
}



void sendHallSensors() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | (GET_HALL_SENSORS <<  1);
    packet_to_send = packet_to_send | (hall_sensors_state[0] << 5);
    packet_to_send = packet_to_send | (hall_sensors_state[1] << 4);
    packet_to_send = packet_to_send | (hall_sensors_state[2] << 3);
}

void sendTurnout() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | (GET_TURNOUT <<  1);
    packet_to_send = packet_to_send | (turnout_position << 3);
}


void requestEvent() {
    Wire.write(packet_to_send);
}



void loop() {
    delay(250); // to avoid spamming
    refreshTurnoutPosition();
    refreshHallSensors();
}
