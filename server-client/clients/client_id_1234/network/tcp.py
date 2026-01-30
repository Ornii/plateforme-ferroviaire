import socket
import threading
import time

from config.config import AppConfig
from led.display import print_led_state
from led.state import LedState

# === Protocol constants ======================================================
# Binary packets representing LED states exchanged between server and client

LED_ALL_ON: bytes = b"0111"
LED_GREEN_ON: bytes = b"0110"
LED_RED_ON: bytes = b"0011"
LED_ALL_OFF: bytes = b"0010"

# Set of all valid LED state packets accepted by the server
VALID_LED_PACKETS: set[bytes] = {
    LED_ALL_ON,
    LED_GREEN_ON,
    LED_RED_ON,
    LED_ALL_OFF,
}

# === Keepalive protocol constants ============================================

# Packet sent by the server to check whether the client is still responsive
KEEPALIVE_REQUEST: bytes = b"alive"

# Expected response from the client to a keepalive request
KEEPALIVE_RESPONSE: bytes = b"ok"

# Maximum allowed inactivity duration before considering the client unresponsive
KEEPALIVE_TIMEOUT: float = 5  # seconds

# Delay between connection retry attempts
TIME_TRY_TO_CONNECT = 2  # seconds


class TcpClient:
    """TCP client handling communication with the LED control server.

    This class:
    - Connects to the TCP server
    - Registers itself using a unique client ID
    - Sends and receives LED state packets
    - Handles keepalive messages
    - Manages user input and display updates
    """

    def __init__(self, led_state: LedState, config: AppConfig):
        """Initialize the TCP client.

        Args:
            led_state: Object storing the current LED state.
            config: Client application configuration.
        """
        self.led_state = led_state
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected_to_server: bool = False
        self.config = config

    def server_registration(self) -> None:
        """Register the client with the TCP server.

        This method:
        - Sends the client ID
        - Waits for server acknowledgment
        - Sends initial LED state
        - Waits for server confirmation
        """
        id_to_send = self.config.tcp_id.encode()
        self.socket.sendall(id_to_send)
        response = ""
        t_end = time.time() + KEEPALIVE_TIMEOUT
        while len(response) == 0 and time.time() < t_end:
            response = self.socket.recv(64)

        if response == b"ok-id":
            self.socket.sendall(self.encode_led_state())
            response = ""
            t_end = time.time() + KEEPALIVE_TIMEOUT
            while len(response) == 0 and time.time() < t_end:
                response = self.socket.recv(64)
            if response != b"ok-led-init":
                raise ValueError(
                    "Server does not respond correctly for led_init registration"
                )
        else:
            raise ValueError("Server does not respond correctly for id registration")

    def decode_led_state(self, packet: bytes) -> None:
        """Decode a received packet and update the LED state.

        Args:
            packet: Raw packet received from the server.
        """
        if packet == LED_ALL_ON:
            self.led_state.set_state(1, 1)
        elif packet == LED_GREEN_ON:
            self.led_state.set_state(1, 0)
        elif packet == LED_RED_ON:
            self.led_state.set_state(0, 1)
        elif packet == LED_ALL_OFF:
            self.led_state.set_state(0, 0)

    def encode_led_state(self) -> bytes:
        """Encode the current LED state into a TCP packet.

        Returns:
            A byte sequence representing the LED state.
        """
        if self.led_state.green == 1 and self.led_state.red == 1:
            return LED_ALL_ON
        elif self.led_state.green == 0 and self.led_state.red == 1:
            return LED_RED_ON
        elif self.led_state.green == 0 and self.led_state.red == 0:
            return LED_ALL_OFF
        else:
            return LED_GREEN_ON

    def receive_loop(self) -> None:
        """Continuously receive packets from the server.

        This loop:
        - Handles LED state updates
        - Responds to keepalive requests
        - Stops on connection reset
        """
        try:
            while True:
                packet = self.socket.recv(64)
                if len(packet) > 0:
                    if packet in VALID_LED_PACKETS:
                        self.receive_led(packet)
                    elif packet == KEEPALIVE_REQUEST:
                        self.receive_alive()
                    else:
                        raise SystemError("Wrong sending of server")
        except ConnectionResetError:
            self.is_connected_to_server = False

    def receive_led(self, packet: bytes) -> None:
        """Handle an incoming LED state packet.

        Args:
            packet: Packet containing LED state information.
        """
        self.decode_led_state(packet)
        print_led_state(self.led_state)
        print(
            f"[{self.config.tcp_id}] - [set green LED state 0(0/1) and set red LED state 1(0/1) (0111 e.g.)] or [get LED state: 2] \n"
        )

    def receive_alive(self) -> None:
        """Respond to a server keepalive request."""
        self.socket.sendall(KEEPALIVE_RESPONSE)

    def send_loop(self) -> None:
        """Handle user input and send LED commands to the server."""
        try:
            while True:
                led_user_input = input(
                    f"[{self.config.tcp_id}] - [set green LED state 0(0/1) and set red LED state 1(0/1) (0111 e.g.)] or [get LED state: 2] \n"
                )
                if led_user_input == "2":
                    print_led_state(self.led_state)
                else:
                    self.send_led(led_user_input)
                    print_led_state(self.led_state)

        except ConnectionResetError:
            self.is_connected_to_server = False

    def send_led(self, led_user_input: str):
        """Send a LED state update to the server.

        Args:
            led_user_input: User-entered LED command.
        """
        if led_user_input not in ["0010", "0011", "0110", "0111"]:
            print(f"[{self.config.tcp_id}] - Please enter 0010, 0011, 0110, 0111 or 2")
        else:
            self.decode_led_state(led_user_input.encode())
            self.socket.sendall(self.encode_led_state())

    def start_connection(self):
        """Establish and maintain the connection to the TCP server.

        This method:
        - Tries to connect to the server
        - Retries on failure
        - Registers the client
        - Starts send and receive threads
        """
        while True:
            if not self.is_connected_to_server:
                print(f"[{self.config.tcp_id}] - Connecting to server...")
                self.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM
                )  # need to refresh socket

                while not self.is_connected_to_server:
                    try:
                        self.socket.connect(
                            (self.config.tcp_server_addr, self.config.tcp_port)
                        )
                        self.server_registration()
                        self.is_connected_to_server = True

                    except ConnectionRefusedError:
                        time.sleep(TIME_TRY_TO_CONNECT)

                print(
                    f"[{self.config.tcp_id}] - \033[35mConnected to {self.config.tcp_server_addr}\033[37m"
                )

                threading.Thread(
                    target=self.send_loop,
                    daemon=True,
                    name=f"TCP-Sender-{self.config.tcp_id}",
                ).start()

                threading.Thread(
                    target=self.receive_loop,
                    daemon=True,
                    name=f"TCP-Receiver-{self.config.tcp_id}",
                ).start()
