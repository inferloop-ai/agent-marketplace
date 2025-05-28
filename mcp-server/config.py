# mcp-server/config.py
import os
from typing import List, Optional
from pydantic import BaseSettings, Field

class MCPSettings(BaseSettings):
    """MCP Server configuration settings."""
    
    # Server
    host: str = Field(default="0.0.0.0", env="MCP_HOST")
    port: int = Field(default=8080, env="MCP_PORT")
    debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Security
    secret_key: str = Field(env="MCP_SECRET_KEY")
    admin_token: str = Field(env="MCP_ADMIN_TOKEN")
    backend_token: str = Field(env="MCP_BACKEND_TOKEN")
    
    # Context Storage
    context_ttl: int = Field(default=86400, env="CONTEXT_TTL")  # 24 hours
    max_context_size: int = Field(default=1048576, env="MAX_CONTEXT_SIZE")  # 1MB
    
    # Extensions
    enable_extensions: bool = Field(default=True, env="ENABLE_EXTENSIONS")
    extensions_dir: str = Field(default="./extensions", env="EXTENSIONS_DIR")
    
    # Logging
    log_level: str = Field(default="INFO", env="MCP_LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="MCP_LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="MCP_LOG_FILE")
    log_rotation: str = Field(default="midnight", env="MCP_LOG_ROTATION")
    log_retention: int = Field(default=7, env="MCP_LOG_RETENTION")

    # Metrics
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")

    # CORS
    allow_origins: List[str] = Field(default_factory=lambda: ["*"], env="ALLOW_ORIGINS")
    allow_credentials: bool = Field(default=True, env="ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default_factory=lambda: ["*"], env="ALLOW_METHODS")
    allow_headers: List[str] = Field(default_factory=lambda: ["*"], env="ALLOW_HEADERS")

    class Config:
        """Pydantic model configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = MCPSettings()
