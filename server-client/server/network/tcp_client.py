from __future__ import annotations

import socket
import time

from led.led_state import LedState

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

# Delay between keepalive request and next check
KEEPALIVE_RETRY_DELAY: float = 1  # seconds


class ConnectedClient:
    """
    Represents a TCP-connected client and maintains its state.

    This class is responsible for:
    - Tracking the LED state associated with the client
    - Receiving and decoding packets from the client
    - Maintaining keepalive state and detecting disconnections
    """

    def __init__(self, conn: socket.socket, addr: socket._RetAddress):
        """
        Initialize a newly connected client.

        Args:
            conn: Active TCP socket connected to the client
            addr: Client network address (IP, port)
        """
        self.led_state: LedState = LedState()
        self.address: tuple[str, int] = addr
        self.connection: socket.socket = conn
        self.client_id: str = "Unknown"
        self.is_connected: bool = True
        self.last_keepalive: float = time.time()

    def encode_led_state(self) -> bytes:
        """
        Encode the current LED state into a protocol packet.

        Returns:
            bytes: Binary packet representing the LED state
        """
        if self.led_state.green == 1 and self.led_state.red == 1:
            return LED_ALL_ON
        elif self.led_state.green == 0 and self.led_state.red == 1:
            return LED_RED_ON
        elif self.led_state.green == 0 and self.led_state.red == 0:
            return LED_ALL_OFF
        else:
            return LED_GREEN_ON

    def decode_led_state(self, packet: bytes) -> None:
        """
        Decode a received LED state packet and update internal LED state.

        Args:
            packet: Binary packet representing an LED state
        """
        if packet == LED_ALL_ON:
            self.led_state.set_state(1, 1)
        elif packet == LED_GREEN_ON:
            self.led_state.set_state(1, 0)
        elif packet == LED_RED_ON:
            self.led_state.set_state(0, 1)
        elif packet == LED_ALL_OFF:
            self.led_state.set_state(0, 0)

    def receive_loop(self) -> None:
        """
        Main receive loop for the client connection.

        Continuously reads packets from the socket and dispatches them
        according to the protocol (LED state updates or keepalive responses).
        """
        try:
            while self.is_connected:
                packet = self.connection.recv(64)
                if len(packet) > 0:
                    if packet in VALID_LED_PACKETS:
                        self.decode_led_state(packet)
                    elif packet == KEEPALIVE_RESPONSE:
                        self.last_keepalive = time.time()
                    else:
                        raise ValueError("Invalid packet received from client")

        except ConnectionResetError:
            self.is_connected = False

    def keepalive_loop(self, tcp_server: TcpServer) -> None:
        """
        Periodically checks client responsiveness using keepalive packets.

        If the client fails to respond within the configured timeout,
        the client is marked as disconnected and removed from the server.
        """
        while self.is_connected:
            if time.time() - self.last_keepalive > KEEPALIVE_TIMEOUT:
                try:
                    self.connection.sendall(KEEPALIVE_REQUEST)
                    time.sleep(KEEPALIVE_RETRY_DELAY)

                except ConnectionError:
                    self.is_connected = False

        print(f"Client id {self.client_id} is disconnected")
        del tcp_server.connected_clients[self.client_id]
