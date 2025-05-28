"""
MCP Server Extensions Package
===========================

This package contains the extension system for the MCP Server, allowing for custom functionality
and integration points.

Features:
- Extension loading and management
- Hook system for extending server functionality
- Plugin architecture for custom features
"""

from .extension_manager import ExtensionManager
from .base_extension import BaseExtension

__all__ = ['ExtensionManager', 'BaseExtension']
