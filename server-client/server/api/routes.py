import logging
import os
import sys

from config.config import AppConfig
from network.tcp_server import TcpServer

from flask import Flask, Response, jsonify, render_template, request


def hide_flask_logs() -> None:
    """
    Disable Flask and Werkzeug default logs.

    This function reduces console noise by:
    - Setting Werkzeug logger level to ERROR
    - Hiding the Flask startup banner
    """
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None


def register_routes(
    app: Flask, tcp_server: TcpServer, config: AppConfig, BASE_DIR: str
) -> None:
    """
    Register all HTTP routes for the Flask web application.

    This function:
    - Optionally disables Flask logs
    - Registers HTML rendering routes
    - Registers REST API endpoints to interact with TCP clients

    Args:
        app: The Flask application instance.
        tcp_server: The TCP server managing connected clients.
        config: Application configuration.
        BASE_DIR: Directory of base files.
    """
    os.chdir(BASE_DIR)
    if not config.web_logs:
        hide_flask_logs()

    @app.route("/")
    def render_index() -> str:
        """
        Render the main index page.

        Returns:
            The rendered HTML index page.
        """
        return render_template("index.html")

    @app.route("/api/clients", methods=["GET"])
    def get_connected_clients() -> Response:
        """
        Retrieve the list of currently connected TCP clients.

        Returns:
            A JSON object mapping indices to client IDs.
        """
        connected_clients_dict = {}
        for index, client_id in enumerate(tcp_server.connected_clients.keys()):
            connected_clients_dict[f"{index}"] = client_id
        return jsonify(connected_clients_dict)

    @app.route("/clients/<client_id>")
    def client_control_page(client_id):
        """
        Render the LED control page for a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            The rendered control page if the client exists,
            otherwise an HTTP 400 error.
        """
        if client_id in tcp_server.connected_clients:
            return render_template("client_control.html", client_id=client_id)
        else:
            return "Error - Bad request", 400

    @app.route("/api/clients/<client_id>/define_state", methods=["POST"])
    def set_client_led_state(client_id: str) -> Response:
        """
        Update the LED state of a specific client.

        Expected JSON payload format:
            {
                "green_led_state": int,
                "red_led_state": int
            }

        Accepted values:
            0 or 1 for explicit state
            -1 to keep the current state

        Args:
            client_id: The unique identifier of the client.

        Returns:
            A JSON response indicating success or failure.
        """
        if client_id in tcp_server.connected_clients:
            payload = request.get_json()

            if list(payload.keys()) != ["green_led_state", "red_led_state"]:
                return jsonify({"error": "Invalid dictionary"})

            green = payload["green_led_state"]
            red = payload["red_led_state"]

            if green not in [0, 1, -1] or red not in [0, 1, -1]:
                return jsonify({"error": "Invalid LED state in dictionary"})

            if green == -1:
                green = tcp_server.connected_clients[client_id].led_state.green
            if red == -1:
                red = tcp_server.connected_clients[client_id].led_state.red

            tcp_server.connected_clients[client_id].led_state.set_state(green, red)

            try:
                tcp_server.connected_clients[client_id].connection.sendall(
                    tcp_server.connected_clients[client_id].encode_led_state()
                )
            except ConnectionResetError:
                tcp_server.connected_clients[client_id].is_connected = False

            return jsonify({"status": "ok"})
        else:
            return jsonify({"client": "disconnected"})

    @app.route("/api/clients/<client_id>/get_state", methods=["GET"])
    def get_client_led_state(client_id: str) -> Response:
        """
        Retrieve the current LED state of a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            A JSON object containing the LED states,
            or a disconnected status.
        """
        if client_id in tcp_server.connected_clients:
            return jsonify(
                {
                    "green_led_state": tcp_server.connected_clients[
                        client_id
                    ].led_state.green,
                    "red_led_state": tcp_server.connected_clients[
                        client_id
                    ].led_state.red,
                }
            )
        else:
            return jsonify({"client": "disconnected"})
