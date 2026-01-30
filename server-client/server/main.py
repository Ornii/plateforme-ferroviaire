import threading
from pathlib import Path

from api.routes import register_routes
from config.config import AppConfig
from network.tcp_server import TcpServer

from flask import Flask

BASE_DIR = str(Path(__file__).parent.resolve())
CONFIG_PATH = rf"{BASE_DIR}\config\config.yaml"


def main():
    """Application entry point.

    This function:
    - Loads the application configuration
    - Starts the TCP server in a background thread
    - Initializes the Flask application
    - Registers HTTP routes
    - Starts the web server
    """
    config = AppConfig.load_from_yaml(CONFIG_PATH)
    tcp_server = TcpServer(config)

    threading.Thread(
        target=tcp_server.start_accept_loop, daemon=True, name="TCP-Server"
    ).start()

    app = Flask(__name__)

    register_routes(app, tcp_server, config, BASE_DIR)

    app.run(
        host=config.web_addr,
        port=config.web_port,
        debug=config.web_debug,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
