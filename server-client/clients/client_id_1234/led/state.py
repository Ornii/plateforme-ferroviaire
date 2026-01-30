from config.config import AppConfig


class LedState:
    def __init__(self, config: AppConfig):
        self.green: int = config.led_green_init
        self.red: int = config.led_green_init

    def set_state(self, green: int, red: int) -> None:
        if green not in (0, 1) or red not in (0, 1):
            raise ValueError("LEDs state must be 0 or 1")
        self.green = green
        self.red = red

    def turn_green_on(self) -> None:
        self.set_state(1, 0)

    def turn_red_on(self) -> None:
        self.set_state(0, 1)
