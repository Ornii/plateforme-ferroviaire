import yaml


class AppConfig:
    """Client-side application configuration.

    This class stores:
    - TCP client configuration
    - Initial LED states

    Attributes:
        tcp_server_addr: Address of the TCP server.
        tcp_port: TCP server port.
        tcp_id: Unique identifier of the client.
        led_green_init: Initial green LED state.
        led_red_init: Initial red LED state.
    """

    def __init__(self, tcp: dict, led: dict):
        self.tcp_server_addr: str = tcp.get("server_address", "0.0.0.0")
        self.tcp_port: int = tcp.get("port", 1234)
        self.tcp_id: str = str(tcp.get("id", "not-assigned"))
        self.led_green_init: int = led.get("green_led_init_state", 0)
        self.led_red_init: int = led.get("red_led_init_state", 0)

    @classmethod
    def load_from_yaml(cls, file_name: str):
        """Load client configuration from a YAML file.

        Args:
            file_name: Path to the YAML configuration file.

        Returns:
            An initialized AppConfig instance.
        """
        with open(file_name, "r") as file:
            data_loaded = yaml.safe_load(file)

        tcp = data_loaded.get("tcp", {})
        led = data_loaded.get("led", {})

        return cls(tcp, led)
