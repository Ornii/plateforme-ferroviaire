import socket
from time import sleep

from smbus2 import SMBus

"""I2C Connection"""
GREEN_ADDR = 0x8
RED_ADDR = 0x9
bus = SMBus(1)  # chose /dev/ic2-1

"""TCP Connection"""
PORT = 1024
IP = "192.168.40.108"

"""Print variable"""
GREEN_COLOR_ON = "Green: On"
GREEN_COLOR_OFF = "Green: Off"
GREEN_COLOR = "Green"

RED_COLOR_ON = "Red: On"
RED_COLOR_OFF = "Red: Off"
RED_COLOR = "Red"


def print_led_state():
    print("------État du feu------")
    if green_led_state:
        print(GREEN_COLOR_ON)
        s.sendall(b"01")
    else:
        print(GREEN_COLOR_OFF)
        s.sendall(b"00")

    if red_led_state:
        print(RED_COLOR_ON)
        s.sendall(b"11")
    else:
        print(RED_COLOR_OFF)
        s.sendall(b"10")


def print_led_color():
    print("------Siganl color------")
    if green_led_state:
        print(GREEN_COLOR)
        s.sendall(b"01")
    else:
        print(RED_COLOR)
        s.sendall(b"10")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))

    green_data_read = bus.read_byte(GREEN_ADDR)
    red_data_read = bus.read_byte(RED_ADDR)

    green_led_state = bool(green_data_read)
    red_led_state = bool(red_data_read)

    print("------Phase initiale------")
    print_led_state()

    if green_led_state and red_led_state:
        green_led_state = False
        bus.write_byte(GREEN_ADDR, 0x0)

    elif not green_led_state and not red_led_state:
        green_led_state = True
        bus.write_byte(GREEN_ADDR, 0x1)

    print("------Start loop------")
    print_led_state()

    while True:
        sleep(0.5)

        green_data_read = bus.read_byte(GREEN_ADDR)
        green_led_state_new = bool(green_data_read)

        if green_led_state != green_led_state_new:
            if green_led_state_new:
                bus.write_byte(RED_ADDR, 0x0)
                red_led_state = False
            else:
                bus.write_byte(RED_ADDR, 0x1)
                red_led_state = True

            green_led_state = green_led_state_new

        red_data_read = bus.read_byte(RED_ADDR)
        red_led_state_new = bool(red_data_read)

        if red_led_state != red_led_state_new:
            if red_led_state_new:
                bus.write_byte(GREEN_ADDR, 0x0)
                green_led_state = False
            else:
                bus.write_byte(GREEN_ADDR, 0x1)
                green_led_state = True

            red_led_state = red_led_state_new
        print_led_state()
