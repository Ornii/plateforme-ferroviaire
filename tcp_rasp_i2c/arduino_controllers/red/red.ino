#include <Wire.h>

const int RED_LED_PIN = 13;
bool red_led_state;

void setup() {
  Wire.begin(0x08);
  Serial.begin(9600);

  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);

  pinMode(RED_LED_PIN, OUTPUT);
  digitalWrite(RED_LED_PIN, LOW);
  red_led_state = false;
}

void receiveEvent() {

  if (Wire.available()) {
    uint8_t packet = Wire.read();
  }
  digitalWrite(RED_LED_PIN, packet);

  if (packet == 1) {
    red_led_state = true;
  } else {
    red_led_state = false
  }
}

void requestEvent() {
  if (red_led_state == true) {
    Wire.write(1);
  } else {
    Wire.write(0);
  }
}

void loop() { delay(100); }
