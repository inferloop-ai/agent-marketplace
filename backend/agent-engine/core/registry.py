"""Registry for Agent Engine components."""

from typing import Dict, Type, Any

_registry: Dict[str, Type[Any]] = {}


def register(component: Type[Any]) -> None:
    """Register a component with the registry."""
    _registry[component.__name__] = component


def get(component_name: str) -> Type[Any]:
    """Get a component from the registry by name."""
    return _registry[component_name]
