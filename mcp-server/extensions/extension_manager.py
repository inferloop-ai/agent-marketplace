"""
Extension Manager
===============

Manages loading, unloading, and executing hooks for MCP Server extensions.
"""

import importlib
import os
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from .base_extension import BaseExtension

logger = logging.getLogger(__name__)


class ExtensionManager:
    """
    Manages MCP Server extensions.
    
    Features:
    - Dynamic extension loading
    - Hook system for extension functionality
    - Extension lifecycle management
    """
    
    def __init__(self, extensions_dir: str):
        """
        Initialize the extension manager.
        
        Args:
            extensions_dir: Directory containing extensions
        """
        self.extensions_dir = Path(extensions_dir)
        self.extensions: Dict[str, BaseExtension] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    async def load_extensions(self) -> None:
        """
        Load all extensions from the extensions directory.
        
        Extensions must be in the format:
        - extensions/{extension_name}.py
        - extensions/{extension_name}/__init__.py
        """
        try:
            if not self.extensions_dir.exists():
                logger.warning(f"Extensions directory not found: {self.extensions_dir}")
                return
            
            for entry in self.extensions_dir.iterdir():
                if entry.is_dir() and (entry / "__init__.py").exists():
                    extension_name = entry.name
                    try:
                        module = importlib.import_module(f"extensions.{extension_name}")
                        extension_class = getattr(module, "Extension", None)
                        if extension_class and issubclass(extension_class, BaseExtension):
                            extension = extension_class()
                            self.extensions[extension_name] = extension
                            logger.info(f"Loaded extension: {extension_name}")
                            
                            # Register hooks
                            for hook_name, callback in extension.hooks.items():
                                if hook_name not in self.hooks:
                                    self.hooks[hook_name] = []
                                self.hooks[hook_name].append(callback)
                    except Exception as e:
                        logger.error(f"Failed to load extension {extension_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to load extensions: {e}")
    
    async def trigger_hook(self, hook_name: str, **kwargs) -> None:
        """
        Trigger a hook across all registered extensions.
        
        Args:
            hook_name: Name of the hook to trigger
            **kwargs: Arguments to pass to the hook callbacks
        """
        if hook_name not in self.hooks:
            return
            
        for callback in self.hooks[hook_name]:
            try:
                await callback(**kwargs)
            except Exception as e:
                logger.error(f"Failed to execute hook {hook_name}: {e}")
    
    async def enable_extension(self, extension_name: str) -> bool:
        """
        Enable an extension.
        
        Args:
            extension_name: Name of the extension to enable
            
        Returns:
            bool: True if enabled successfully, False otherwise
        """
        extension = self.extensions.get(extension_name)
        if extension:
            await extension.enable()
            logger.info(f"Enabled extension: {extension_name}")
            return True
        return False
    
    async def disable_extension(self, extension_name: str) -> bool:
        """
        Disable an extension.
        
        Args:
            extension_name: Name of the extension to disable
            
        Returns:
            bool: True if disabled successfully, False otherwise
        """
        extension = self.extensions.get(extension_name)
        if extension:
            await extension.disable()
            logger.info(f"Disabled extension: {extension_name}")
            return True
        return False
    
    def get_extension_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all loaded extensions."""
        return [ext.get_metadata() for ext in self.extensions.values()]
    
    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """Get a specific extension by name."""
        return self.extensions.get(name)
    
    def has_extension(self, name: str) -> bool:
        """Check if an extension is loaded."""
        return name in self.extensions
