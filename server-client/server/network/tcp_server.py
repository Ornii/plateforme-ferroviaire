import socket
import threading

from config.config import AppConfig

from network.tcp_client import ConnectedClient


class TcpServer:
    """
    TCP server responsible for accepting client connections and managing them.

    This server:
    - Accepts incoming TCP connections
    - Performs an initial handshake with each client
    - Stores connected clients
    - Starts communication and keepalive threads for each client
    """

    def __init__(self, config: AppConfig):
        """
        Initialize the TCP server.

        Args:
            config: Application configuration containing network parameters.
        """
        self.config = config
        self.connected_clients: dict[str, ConnectedClient] = {}
        self.server_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.server_socket.bind(("", self.config.tcp_port))
        self.server_socket.listen()

    def handshake_client(self, client: ConnectedClient) -> bool:
        """
        Perform the initial handshake with a connected client.

        The handshake consists of:
        - Receiving the client ID
        - Acknowledging the client ID
        - Receiving the initial LED state
        - Acknowledging the LED state

        Args:
            client: The newly connected client.

        Returns:
            True if the handshake completed successfully, False otherwise.
        """
        packet = client.connection.recv(64)
        if len(packet) > 0:
            client.client_id = packet.decode()
            client.connection.sendall(b"ok-id")
            packet = client.connection.recv(64)
            if len(packet) > 0:
                client.decode_led_state(packet)
                client.connection.sendall(b"ok-led-init")
                return True
        return False

    def start_accept_loop(self) -> None:
        """
        Start the main loop accepting incoming TCP connections.

        For each accepted connection:
        - Perform a handshake
        - Register the client
        - Start receiver and keepalive threads
        """
        print("Waiting for TCP client...")
        while True:
            conn: socket.socket
            addr: tuple[str, int]
            conn, addr = self.server_socket.accept()
            client = ConnectedClient(conn, addr)
            handshake = self.handshake_client(client)
            if not handshake:
                continue
            self.connected_clients[client.client_id] = client

            print(f"\033[35mConnected with id-{client.client_id}\033[37m")

            threading.Thread(
                target=self.connected_clients[client.client_id].receive_loop,
                daemon=True,
                name=f"TCP-Receiver-{client.client_id}",
            ).start()

            threading.Thread(
                target=self.connected_clients[client.client_id].keepalive_loop,
                args=(self,),
                daemon=True,
                name=f"TCP-Check-Alive-{client.client_id}",
            ).start()
