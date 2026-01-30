class LedState:
    """Represents the state of a bi-color LED.

    The LED can be either green, red, both, or off.
    A value of -1 indicates that the LED state is unknown or uninitialized.
    """

    def __init__(self):
        """Initialize the LED state.

        By default, both LED colors are set to -1, meaning the state is unknown.
        """
        self.green: int = -1
        self.red: int = -1

    def set_state(self, green: int, red: int) -> None:
        """Set the state of the green and red LEDs.

        Args:
            green: State of the green LED (0 = off, 1 = on).
            red: State of the red LED (0 = off, 1 = on).

        Raises:
            ValueError: If either value is not 0 or 1.
        """
        if green not in (0, 1) or red not in (0, 1):
            raise ValueError("LEDs state must be 0 or 1")
        self.green = green
        self.red = red

    def turn_green_on(self) -> None:
        """Turn on the green LED and turn off the red LED."""
        self.set_state(1, 0)

    def turn_red_on(self) -> None:
        """Turn on the red LED and turn off the green LED."""
        self.set_state(0, 1)
