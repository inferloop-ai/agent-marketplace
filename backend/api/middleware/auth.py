class DatabaseSettings:
    """
    Configuration class for database settings.
    
    This class manages database connection parameters and configuration options
    for the application. It handles connection strings, pooling settings,
    and other database-related configuration.
    
    Attributes:
        connection_string (str): Database connection URI
        pool_size (int): Maximum number of connections in the pool
        max_overflow (int): Maximum overflow connections allowed
        pool_timeout (int): Timeout for acquiring connections from the pool
        echo (bool): Whether to echo SQL queries (for debugging)
        ssl_mode (str): SSL mode for database connections
    """
    def __init__(self, connection_string: str, pool_size: int = 50, max_overflow: int = 20, pool_timeout: int = 30, echo: bool = False, ssl_mode: str = 'prefer'):
        """
        Initialize DatabaseSettings with given parameters
        
        Args:
            connection_string (str): Database connection URI
            pool_size (int): Maximum number of connections in the pool
            max_overflow (int): Maximum overflow connections allowed
            pool_timeout (int): Timeout for acquiring connections from the pool
            echo (bool): Whether to echo SQL queries (for debugging)
            ssl_mode (str): SSL mode for database connections
        """
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.echo = echo
        self.ssl_mode = ssl_mode
        """
        Returns a dictionary containing the database settings as key-value pairs
        
        Returns:
            dict: A dictionary with the following keys:
                - connection_string
                - pool_size
                - max_overflow
                - pool_timeout
                - echo
                - ssl_mode
        """
        return {
            'connection_string': self.connection_string,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'echo': self.echo,
            'ssl_mode': self.ssl_mode
        }
