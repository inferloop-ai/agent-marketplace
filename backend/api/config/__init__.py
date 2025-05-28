"""
Configuration module for the API.

This module contains functions and classes for loading and managing
configuration settings for the API.

The configuration is loaded from environment variables and a JSON file.
The environment variables take precedence over the values in the JSON file.

The configuration is divided into sections, each section is a class
with attributes for each setting.

The available sections are:

- `database`: Database connection settings.
- `logging`: Logging settings.
- `security`: Security settings.
- `server`: Server settings.

The available settings for each section are:

- `database`:
  - `connection`: The database connection string.
- `logging`:
  - `level`: The logging level.
- `security`:
  - `secret_key`: The secret key used for signing and verifying tokens.
- `server`:
  - `host`: The server host.
  - `port`: The server port.

Example:
    import os
    from backend.api.config import database, logging, security, server

    # Load configuration from environment variables and JSON file
    database.load()
    logging.load()
    security.load()
    server.load()

    # Get the database connection string
    connection = database.connection

    # Set the logging level
    logging.level = os.environ.get("LOGGING_LEVEL", "INFO")

    # Get the secret key
    secret_key = security.secret_key

    # Set the server host and port
    server.host = os.environ.get("SERVER_HOST", "localhost")
    server.port = int(os.environ.get("SERVER_PORT", 8000))

"""

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .database import DatabaseConfig
from .logging import LoggingConfig
from .security import SecurityConfig
from .server import ServerConfig


@dataclass
class Config:
    """
    Base class for configuration sections.

    Attributes:
        name (str): The name of the section.
        settings (Dict[str, Any]): The settings for the section.
    """

    name: str
    settings: Dict[str, Any]

    @classmethod
    def load(cls) -> "Config":
        """
        Load the configuration from environment variables and JSON file.

        Returns:
            Config: The loaded configuration.
        """
        # Load from environment variables
        settings = {}
        for key, value in os.environ.items():
            if key.startswith(cls.name.upper()):
                settings[key.lower()] = value

        # Load from JSON file
        file_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(file_path):
            with open(file_path) as file:
                json_settings = json.load(file)
                settings.update(json_settings.get(cls.name, {}))

        return cls(settings=settings)

    def __getattr__(self, name: str) -> Any:
        """
        Get a setting value.

        Args:
            name (str): The name of the setting.

        Returns:
            Any: The value of the setting.
        """
        return self.settings.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            name (str): The name of the setting.
            value (Any): The value of the setting.
        """
        if name not in self.settings:
            raise AttributeError(f"{self.name} has no attribute {name}")
        self.settings[name] = value
