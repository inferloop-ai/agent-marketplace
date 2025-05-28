class DatabaseSettings:
    """
    Configuration settings for database connections.
    
    This class provides centralized configuration for database connection parameters
    including host, port, credentials, connection pool settings, and timeout values.
    It supports multiple database engines and environments.
    """
    pass
    """
    Configuration settings for database connections.

    This class provides centralized configuration for database connection parameters
    including host, port, credentials, connection pool settings, and timeout values.
    It supports multiple database engines and environments.
    """
    database_url: str = "postgresql://postgres:postgres@localhost:5432/agent_workflows"
    """
    URL of the database for the workflow builder.

    This URL is used to connect to the database used by the workflow builder.
    """
    database_max_connections: int = 100
    """
    Maximum number of connections to the database.

    This setting limits the number of connections made to the database.
    """
    database_max_overflow: int = 0
    """
    Maximum number of connections to the database beyond the pool size.

    This setting limits the number of connections made to the database beyond the
    pool size.
    """
    database_pool_recycle: int = 300
    """
    Time in seconds after which database connections are closed.

    This setting is used to limit the lifetime of database connections.
    """
    database_connect_timeout: int = 10
    """
    Time in seconds to wait for a database connection.

    This setting is used to limit the time to wait for a database connection.
    """
