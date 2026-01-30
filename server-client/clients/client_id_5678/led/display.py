from led.state import LedState

GREEN_ON_MSG = "\033[32m Green: On\033[37m"
GREEN_OFF_MSG = "Green: Off"

RED_ON_MSG = "\033[31mRouge: On\033[37m"
RED_OFF_MSG = "Red: Off"


def print_led_state(led_state: LedState) -> None:
    print("\n------State traffic light------")
    if led_state.green == 1:
        print(GREEN_ON_MSG)
    else:
        print(GREEN_OFF_MSG)

    if led_state.red == 1:
        print(RED_ON_MSG)
    else:
        print(RED_OFF_MSG)
    print("-----------------------\n")
