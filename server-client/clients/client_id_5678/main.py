from pathlib import Path

from config.config import AppConfig
from led.state import LedState
from network.tcp import TcpClient

BASE_DIR = str(Path(__file__).parent.resolve())
CONFIG_PATH = rf"{BASE_DIR}\config\config.yaml"


def main():
    """Client application entry point.

    This function:
    - Loads the client configuration from a YAML file
    - Initializes the LED state
    - Creates a TCP client
    - Starts the TCP connection to the server
    """
    config = AppConfig.load_from_yaml(CONFIG_PATH)
    led_state = LedState(config)
    tcp_client = TcpClient(led_state, config)
    tcp_client.start_connection()


if __name__ == "__main__":
    main()
