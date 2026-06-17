#include <Servo.h>


const int GREEN_LED_1_PIN = 2;
const int RED_LED_1_PIN = 3;
const int HALL_SENSOR_1_PIN = 4;

const int GREEN_LED_2_PIN = 5;
const int RED_LED_2_PIN = 6;
const int HALL_SENSOR_2_PIN = 7;

const int GREEN_LED_3_PIN = 8;
const int RED_LED_3_PIN = 9;
const int HALL_SENSOR_3_PIN = 10;

const int GREEN_LED_4_PIN = 11;
const int RED_LED_4_PIN = 12;
const int HALL_SENSOR_4_PIN = 13;

const int TENSION_TURNOUT_PIN = A0;
const int SERVO_TURNOUT_PIN = 14;
const int TURNOUT_SERVO_ANGLE_1 = 30;
const int TURNOUT_SERVO_ANGLE_2 = 60;

const unsigned long BAUDRATE = 9600;
const int LOOP_DELAY_MS = 2000;
int tension_turnout = 0;

int hall_sensor_1_state = 0;
int hall_sensor_2_state = 0;
int hall_sensor_3_state = 0;
int hall_sensor_4_state = 0;

Servo servo_turnout;


void setup() {
    Serial.begin(BAUDRATE);
    pinMode(GREEN_LED_1_PIN, OUTPUT);
    pinMode(RED_LED_1_PIN, OUTPUT);
    pinMode(HALL_SENSOR_1_PIN, INPUT);

    pinMode(GREEN_LED_2_PIN, OUTPUT);
    pinMode(RED_LED_2_PIN, OUTPUT);
    pinMode(HALL_SENSOR_2_PIN, INPUT);

    pinMode(GREEN_LED_3_PIN, OUTPUT);
    pinMode(RED_LED_3_PIN, OUTPUT);
    pinMode(HALL_SENSOR_3_PIN, INPUT);

    pinMode(GREEN_LED_4_PIN, OUTPUT);
    pinMode(RED_LED_4_PIN, OUTPUT);
    pinMode(HALL_SENSOR_4_PIN, INPUT);

    servo_turnout.attach(SERVO_TURNOUT_PIN);
}

void loop() {
    Serial.println("Talon all HIGH");
    digitalWrite(GREEN_LED_1_PIN, HIGH);
    digitalWrite(RED_LED_1_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_1_PIN, LOW);
    digitalWrite(RED_LED_1_PIN, LOW);

    Serial.println("2 all HIGH");
    digitalWrite(GREEN_LED_2_PIN, HIGH);
    digitalWrite(RED_LED_2_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_2_PIN, LOW);
    digitalWrite(RED_LED_2_PIN, LOW);

    Serial.println("3 all HIGH");
    digitalWrite(GREEN_LED_3_PIN, HIGH);
    digitalWrite(RED_LED_3_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_3_PIN, LOW);
    digitalWrite(RED_LED_3_PIN, LOW);

    Serial.println("4 all HIGH");
    digitalWrite(GREEN_LED_4_PIN, HIGH);
    digitalWrite(RED_LED_4_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_4_PIN, LOW);
    digitalWrite(RED_LED_4_PIN, LOW);

    Serial.println("Servo position 1");
    servo_turnout.write(TURNOUT_SERVO_ANGLE_1);
    delay(LOOP_DELAY_MS);

    Serial.println("Servo position 2");
    servo_turnout.write(TURNOUT_SERVO_ANGLE_2);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured tension:");
    tension_turnout = analogRead(TENSION_TURNOUT_PIN);
    Serial.println(tension_turnout);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall 1:");
    hall_sensor_1_state = digitalRead(HALL_SENSOR_1_PIN);
    Serial.println(hall_sensor_1_state);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall 2:");
    hall_sensor_2_state = digitalRead(HALL_SENSOR_2_PIN);
    Serial.println(hall_sensor_2_state);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall 3:");
    hall_sensor_3_state = digitalRead(HALL_SENSOR_3_PIN);
    Serial.println(hall_sensor_3_state);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall 4:");
    hall_sensor_4_state = digitalRead(HALL_SENSOR_4_PIN);
    Serial.println(hall_sensor_4_state);
    delay(LOOP_DELAY_MS);

}
