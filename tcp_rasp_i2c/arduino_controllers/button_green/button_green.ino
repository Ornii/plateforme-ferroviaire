#include <Wire.h>

const int BUTTON_PIN = A0;
const int GREEN_LED_PIN = 2;
const int TENSION_BUTTON_THRESHOLD = 1000;

int button_tension;
bool green_led_state;
bool must_wait = false; // to avoid led flashes

void setup() {
  Wire.begin(0x09);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  pinMode(GREEN_LED_PIN, OUTPUT);
}

void receiveEvent() {
  if (Wire.available()) {
    uint8_t packet = Wire.read();
  }
  digitalWrite(GREEN_LED_PIN, packet);
  if (packet == 1) {
    green_led_state = true;
  } else {
    green_led_state = false
  }
}

void requestEvent() {
  if (green_led_state == true) {
    Wire.write(1);
  } else {
    Wire.write(0);
  }
}

void loop() {
  button_tension = analogRead(BUTTON_PIN);

  if (button_tension >= TENSION_BUTTON_THRESHOLD && green_led_state == false &&
      must_wait == false) {
    green_led_state = true;
    must_wait = true;
    digitalWrite(green_led_state, HIGH);

  } else if (button_tension >= TENSION_BUTTON_THRESHOLD &&
             green_led_state == true && must_wait == false) {
    green_led_state = false;
    must_wait = true;
    digitalWrite(green_led_state, LOW);
  }

  if (valTension < TENSION_BUTTON_THRESHOLD) {
    must_wait = false;
  }
}
