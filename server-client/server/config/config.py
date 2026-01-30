from __future__ import annotations
import yaml


class AppConfig:
    """Central application configuration loaded from a YAML file.

    This class stores configuration values for:
    - TCP server
    - Web (Flask) server

    Attributes:
        tcp_server_addr: Address on which the TCP server listens.
        tcp_port: Port used by the TCP server.
        web_addr: Address on which the web server listens.
        web_port: Port used by the web server.
        web_debug: Whether Flask debug mode is enabled.
        web_logs: Whether Flask/Werkzeug logs are enabled.
    """

    def __init__(self, tcp: dict, web: dict):
        """Initialize configuration from parsed dictionaries.

        Args:
            tcp: Dictionary containing TCP-related configuration.
            web: Dictionary containing web server configuration.
        """
        self.tcp_server_addr: str = tcp.get("address", "0.0.0.0")
        self.tcp_port: int = tcp.get("port", 1234)
        self.web_addr: str = web.get("address", "0.0.0.0")
        self.web_port: int = web.get("port", 8080)
        self.web_debug: bool = web.get("debug", True)
        self.web_logs: bool = web.get("flask_logs", False)

    @classmethod
    def load_from_yaml(cls, file_name: str) -> AppConfig:
        """Load application configuration from a YAML file.

        Args:
            file_name: Path to the YAML configuration file.

        Returns:
            An initialized AppConfig instance.
        """
        with open(file_name, "r") as file:
            data_loaded = yaml.safe_load(file)

        tcp = data_loaded.get("tcp", {})
        web = data_loaded.get("web", {})

        return cls(tcp, web)
