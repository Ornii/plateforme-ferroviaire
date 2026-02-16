#include <Wire.h>
#include <Servo.h>

// Main track
const int green_led_main_track = 2;
const int red_led_main_track = 3;
const int hall_sensor_main_track = 4;
int hall_sensor_main_track_state = 1;

// Straight track
const int green_led_straight_track = 5;
const int red_led_straight_track = 6;
const int hall_sensor_straight_track = 7;
int hall_sensor_straight_track_state = 1;

// Diverging track
const int green_led_diverging_track = 8;
const int red_led_diverging_track = 9;
const int hall_sensor_diverging_track = 10;
int hall_sensor_diverging_track_state = 1;


// Blade switch
const int tension_blade_switch_pin = A0;
const int servo_blade_switch_pin = 11;
Servo servo_blade_switch;
int mesured_tension_blade_switch;


int packet_to_send = 0; // packet which is modified each time the client received a "get" order and then send

enum FunctionCode {
  SET_LED = 0b00,
  SET_BLADE_SWITCH = 0b01,
  GET_HALL_SENSORS = 0b10,
  GET_BLADE_SWITCH = 0b11
};

enum TrainPosition {
  MAIN_TRACK = 0b000,
  STRAIGHT_TRACK = 0b001,
  DIVERGING_TRACK = 0b010,
  BLADE_SWITCH = 0b011     // intermediary position
};

enum LightState {
  RED = 0b00,
  YELLOW = 0b10,
  GREEN = 0b11
};

enum BladeSwitchState {
    RAIL_STRAIGHT = 0b1,
    RAIL_DIVERGING = 0b0
};

// Variable which describe the current state of sensor
uint8_t hallsState[3] = {
  0, // MAIN_TRACK
  0, // STRAIGHT_TRACK
  0  // DIVERGING_TRACK
};

BladeSwitchState current_blade_switch = RAIL_DIVERGING;

void receiveEvent(int howMany);
void requestEvent();
void setLed(int packet);
void setBladeSwitch(int packet);
void sendHallSensors();
void sendBladeSwitch();


void setup() {
  Wire.begin(0x08);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  // Main track
  pinMode(green_led_main_track, OUTPUT);
  pinMode(red_led_main_track, OUTPUT);
  pinMode(hall_sensor_main_track, INPUT);

  // Straight track
  pinMode(green_led_straight_track, OUTPUT);
  pinMode(red_led_straight_track, OUTPUT);
  pinMode(hall_sensor_straight_track, INPUT);

  // Diverging track
  pinMode(green_led_diverging_track, OUTPUT);
  pinMode(red_led_diverging_track, OUTPUT);
  pinMode(hall_sensor_diverging_track, INPUT);

  // Blade switch
  servo_blade_switch.attach(servo_blade_switch_pin);
  servo_blade_switch.write(15);  // initial neutral position


  Serial.begin(9600);
}



void receiveEvent(int howMany) {
    while (Wire.available()) {
    int packet = Wire.read();
    Serial.println(packet, BIN);

    // decoding the type of packet and then

    FunctionCode function = ((packet >> 1) & 0b11);

    if (function == SET_LED) {
        setLed(packet);
    } else if (function == SET_BLADE_SWITCH) {
        setBladeSwitch(packet);
    } else if (function == GET_BLADE_SWITCH) {
        sendBladeSwitch();
    } else if (function == GET_HALL_SENSORS) {
        sendHallSensors();
    }
    }
}

void setLed(int packet) {
    TrainPosition emplacement = ((packet >> 5) & 0b111);
    LightState color = ((packet >> 3) & 0b11);

   if (emplacement ==  MAIN_TRACK){

       if (color == GREEN) {
           digitalWrite(green_led_main_track, HIGH);
           digitalWrite(red_led_main_track, LOW);

       } else if (color == RED) {
           digitalWrite(green_led_main_track, LOW);
           digitalWrite(red_led_main_track, HIGH);
       }

   } else if (emplacement == STRAIGHT_TRACK) {

       if (color == GREEN) {
           digitalWrite(green_led_straight_track, HIGH);
           digitalWrite(red_led_straight_track, LOW);

       } else if (color == RED) {
           digitalWrite(green_led_straight_track, LOW);
           digitalWrite(red_led_straight_track, HIGH);
       }

   } else if (emplacement == DIVERGING_TRACK) {

       if (color == GREEN) {
           digitalWrite(green_led_diverging_track, HIGH);
           digitalWrite(red_led_diverging_track, LOW);

       } else if (color == RED) {
           digitalWrite(green_led_diverging_track, LOW);
           digitalWrite(red_led_diverging_track, HIGH);
       }
   }
}

void setBladeSwitch(int packet) {
    BladeSwitchState demand_blade_switch_state = ((packet >> 3) & 0b1);

    if (!(demand_blade_switch_state == current_blade_switch)) {
        if (demand_blade_switch_state == RAIL_STRAIGHT) {
            servo_blade_switch.write(15);
        } else if (demand_blade_switch_state == RAIL_DIVERGING){
                servo_blade_switch.write(30);
            }

    }
    current_blade_switch = demand_blade_switch_state;
}

void sendHallSensors() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | (GET_HALL_SENSORS <<  1);
    packet_to_send = packet_to_send | (hallsState[0] << 5);
    packet_to_send = packet_to_send | (hallsState[1] << 4);
    packet_to_send = packet_to_send | (hallsState[2] << 3);
}

void sendBladeSwitch() {
    packet_to_send = 0;
    packet_to_send = packet_to_send | (GET_BLADE_SWITCH <<  1);
    packet_to_send = packet_to_send | (current_blade_switch << 3);
}


void requestEvent() {
    Wire.write(packet_to_send);
    }



void loop() {
  delay(250); // nécessaire pour pas surcharger...
  int hall_sensor_diverging_track_state_new = digitalRead(hall_sensor_diverging_track);
  int hall_sensor_straight_track_state_new = digitalRead(hall_sensor_straight_track);
  int hall_sensor_main_track_state_new = digitalRead(hall_sensor_main_track);
  Serial.println("hall state");
  Serial.println(hall_sensor_main_track_state_new);
  if (!(hall_sensor_diverging_track_state_new == hall_sensor_diverging_track_state) && (hall_sensor_diverging_track_state == 1)) {
      hall_sensor_diverging_track_state = 0;
  }

  if (!(hall_sensor_straight_track_state_new == hall_sensor_straight_track_state) && (hall_sensor_straight_track_state == 1)) {
      hall_sensor_straight_track_state = 0;
  }

  if (!(hall_sensor_main_track_state_new == hall_sensor_main_track_state) && (hall_sensor_main_track_state == 1)) {
      hall_sensor_main_track_state = 0;
  }

  hallsState[0] = hall_sensor_main_track_state ^ 1;
  hallsState[1] = hall_sensor_straight_track_state ^ 1;
  hallsState[2] = hall_sensor_diverging_track_state ^ 1;

  mesured_tension_blade_switch = analogRead(tension_blade_switch_pin);
  if (mesured_tension_blade_switch >= 700) {
      current_blade_switch = RAIL_STRAIGHT;

  } else {
      current_blade_switch = RAIL_DIVERGING;
  }
}
