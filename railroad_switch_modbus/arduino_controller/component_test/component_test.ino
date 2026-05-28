#include <Servo.h>


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
const int TURNOUT_SERVO_DIRECT_ANGLE = 15;
const int TURNOUT_SERVO_DEVIEE_ANGLE = 30;

const unsigned long BAUDRATE = 9600;
const int LOOP_DELAY_MS = 2000;
int tension_turnout = 0;

int hall_sensor_talon_state = 0;
int hall_sensor_direct_state = 0;
int hall_sensor_deviee_state = 0;

Servo servo_turnout;


void setup() {
    Serial.begin(BAUDRATE);
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
}

void loop() {
    Serial.println("Talon all HIGH");
    digitalWrite(GREEN_LED_TALON_PIN, HIGH);
    digitalWrite(RED_LED_TALON_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_TALON_PIN, LOW);
    digitalWrite(RED_LED_TALON_PIN, LOW);

    Serial.println("Direct all HIGH");
    digitalWrite(GREEN_LED_DIRECT_PIN, HIGH);
    digitalWrite(RED_LED_DIRECT_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_DIRECT_PIN, LOW);
    digitalWrite(RED_LED_DIRECT_PIN, LOW);

    Serial.println("Deviee all HIGH");
    digitalWrite(GREEN_LED_DEVIEE_PIN, HIGH);
    digitalWrite(RED_LED_DEVIEE_PIN, HIGH);
    delay(LOOP_DELAY_MS);
    digitalWrite(GREEN_LED_DEVIEE_PIN, LOW);
    digitalWrite(RED_LED_DEVIEE_PIN, LOW);

    Serial.println("Servo position 1");
    servo_turnout.write(TURNOUT_SERVO_DEVIEE_ANGLE);
    delay(LOOP_DELAY_MS);

    Serial.println("Servo position 2");
    servo_turnout.write(TURNOUT_SERVO_DIRECT_ANGLE);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured tension:");
    tension_turnout = analogRead(TENSION_TURNOUT_PIN);
    Serial.println(tension_turnout);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall talon:");
    hall_sensor_talon_state = digitalRead(HALL_SENSOR_TALON_PIN);
    Serial.println(hall_sensor_talon_state);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall direct:");
    hall_sensor_direct_state = digitalRead(HALL_SENSOR_DIRECT_PIN);
    Serial.println(hall_sensor_direct_state);
    delay(LOOP_DELAY_MS);

    Serial.println("Mesured hall deviee:");
    hall_sensor_deviee_state = digitalRead(HALL_SENSOR_DEVIEE_PIN);
    Serial.println(hall_sensor_deviee_state);
    delay(LOOP_DELAY_MS);


}
