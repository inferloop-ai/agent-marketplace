"""
Base Extension Class
===================

Base class for all MCP Server extensions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseExtension(ABC):
    """
    Base class for MCP Server extensions.
    
    Extensions can implement hooks to extend server functionality.
    
    Available Hooks:
    - context_created
    - context_updated
    - context_deleted
    - context_accessed
    - server_started
    - server_shutdown
    """
    
    name: str
    version: str
    description: str
    enabled: bool = True
    hooks: Dict[str, callable] = {}
    
    def __init__(self):
        """Initialize the extension."""
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = """""
        self.enabled = True
        self.hooks = {}
        
        # Register default hooks
        self.register_hook("context_created", self.on_context_created)
        self.register_hook("context_updated", self.on_context_updated)
        self.register_hook("context_deleted", self.on_context_deleted)
        self.register_hook("context_accessed", self.on_context_accessed)
        self.register_hook("server_started", self.on_server_started)
        self.register_hook("server_shutdown", self.on_server_shutdown)
    
    def register_hook(self, hook_name: str, callback: callable) -> None:
        """
        Register a hook callback.
        
        Args:
            hook_name: Name of the hook
            callback: Callback function
        """
        self.hooks[hook_name] = callback
    
    @abstractmethod
    async def on_context_created(self, context_id: str, context_data: Dict[str, Any]) -> None:
        """Called when a new context is created."""
        pass
    
    @abstractmethod
    async def on_context_updated(self, context_id: str, context_data: Dict[str, Any]) -> None:
        """Called when a context is updated."""
        pass
    
    @abstractmethod
    async def on_context_deleted(self, context_id: str, context_data: Dict[str, Any]) -> None:
        """Called when a context is deleted."""
        pass
    
    @abstractmethod
    async def on_context_accessed(self, context_id: str) -> None:
        """Called when a context is accessed."""
        pass
    
    @abstractmethod
    async def on_server_started(self) -> None:
        """Called when the server starts."""
        pass
    
    @abstractmethod
    async def on_server_shutdown(self) -> None:
        """Called when the server shuts down."""
        pass
    
    async def enable(self) -> None:
        """Enable the extension."""
        self.enabled = True
        
    async def disable(self) -> None:
        """Disable the extension."""
        self.enabled = False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "hooks": list(self.hooks.keys())
        }
