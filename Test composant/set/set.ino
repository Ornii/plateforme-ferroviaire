#include <Wire.h>
#include <Servo.h>

// Main track
const int green_led_main_track = 2;
const int red_led_main_track = 3;
const int hall_sensor_main_track = 4;
int hall_sensor_main_track_state = 0;

// Straight track
const int green_led_straight_track = 5;
const int red_led_straight_track = 6;
const int hall_sensor_straight_track = 7;
int hall_sensor_straight_track_state = 0;

// Diverging track
const int green_led_diverging_track = 8;
const int red_led_diverging_track = 9;
const int hall_sensor_diverging_track = 10;
int hall_sensor_diverging_track_state = 0;


// Rail switch
const int tension_rail_switch_pin = A0;
const int servo_rail_switch_pin = 11;
Servo servo_rail_switch;
int mesured_tension_rail_switch;


int packet_to_send = 0; // packet which is modified each time the client received a "get" order and then send

enum FunctionCode {
  SET_LED = 0b00,
  SET_RAIL_SWITCH = 0b01,
  GET_HALL = 0b10,
  GET_RAIL_SWITCH = 0b11
};

enum TrainPosition {
  MAIN_TRACK = 0b000,
  STRAIGHT_TRACK = 0b001,
  DIVERGING_TRACK = 0b010,
  RAIL_SWITCH = 0b011     // intermediary position
};

enum LightState {
  RED = 0b00,
  YELLOW = 0b10,
  GREEN = 0b11
};

enum RailSwitchState {
    RAIL_STRAIGHT = 0b0,
    RAIL_DIVERGING = 0b1
};

// Variable which describe the current state of sensor
uint8_t hallsState[3] = {
  0, // MAIN_TRACK
  0, // STRAIGHT_TRACK
  0  // DIVERGING_TRACK
};

RailSwitchState current_rail_switch = RAIL_DIVERGING;


void setLed(int packet);
void setRailSwitch(int packet);
void sendHalls();
void sendRailSwitch();


void setup() {
  // Main track
  pinMode(green_led_diverging_track, OUTPUT);
  pinMode(red_led_diverging_track, OUTPUT);
  pinMode(hall_sensor_diverging_track, INPUT);

  servo_rail_switch.attach(servo_rail_switch_pin);
  servo_rail_switch.write(90);  // initial neutral position
}

void loop() {
    mesured_tension_rail_switch = analogRead(tension_rail_switch_pin);
    digitalWrite(green_led_diverging_track, mesured_tension_rail_switch >= 700);
    digitalWrite(red_led_diverging_track, mesured_tension_rail_switch <= 700);
    delay(500);
    servo_rail_switch.write(45);
    delay(500);
    servo_rail_switch.write(-45);
}
