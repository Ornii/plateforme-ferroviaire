#include <Servo.h>

Servo monServo;

void setup()
{
  monServo.attach(9);  // relier le servomoteur au port 9
  monServo.write(90);  // positionner le servomoteur à l'angle absolu 90°
}

void loop() {
  delay(1000);
  monServo.write(15);
  delay(1000);
  monServo.write(-15);
}
