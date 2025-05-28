"""
Database configuration
"""

from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Database settings
    """

    host: str = "localhost"
    """
    Database host
    """

    port: int = 5432
    """
    Database port
    """

    username: str = "postgres"
    """
    Database username
    """

    password: str = "postgres"
    """
    Database password
    """

    database: str = "postgres"
    """
    Database name
    """

    async_: bool = True
    """
    Use async database connection
    """

    echo: bool = False
    """
    Echo database queries
    """

    pool_size: int = 20
    """
    Database connection pool size
    """

    max_overflow: int = 10
    """
    Database connection max overflow
    """
