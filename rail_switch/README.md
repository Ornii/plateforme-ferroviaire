# Requirements
-Python on a Raspberry
-Arduino which is connected to the Raspberry with I2C on address `0x08`

## Slave
Before each train, reupload on the Arduino the code `main.ino`. It restores basic values of sensors.

## Master
Then, launch the `main.py` on the Raspberry. The OBJECTIVE list gives the willing path.
