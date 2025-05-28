"""
MCP Server Utilities
===================

Common utility functions for the MCP Server.
"""

import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        str: Unique ID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    return f"{prefix}{timestamp}-{random_part}"


def validate_json(data: Any) -> Dict[str, Any]:
    """
    Validate and normalize JSON data.
    
    Args:
        data: Data to validate
        
    Returns:
        Dict: Validated JSON data
        
    Raises:
        ValueError: If data is not valid JSON
    """
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise ValueError("Invalid JSON data")
    elif isinstance(data, dict):
        return data
    else:
        raise ValueError("Data must be a JSON string or dictionary")


def get_timestamp() -> int:
    """Get current timestamp in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


def format_size(size_bytes: int) -> str:
    """
    Format bytes size into human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}B"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def safe_get(d: Dict, *keys: str, default: Optional[Any] = None) -> Any:
    """
    Safely get nested dictionary value.
    
    Args:
        d: Dictionary to search
        *keys: Keys to access
        default: Default value if keys don't exist
        
    Returns:
        Any: Value or default if not found
    """
    try:
        for key in keys:
            d = d[key]
        return d
    except (KeyError, TypeError):
        return default


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split list into chunks.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        list: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_hash(data: Any) -> str:
    """
    Calculate SHA-256 hash of data.
    
    Args:
        data: Data to hash
        
    Returns:
        str: Hexadecimal hash
    """
    if isinstance(data, str):
        data = data.encode()
    elif isinstance(data, dict):
        data = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
