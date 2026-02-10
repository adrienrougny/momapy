"""Plugin system for momapy.

Provides a generic plugin registry for extending momapy functionality.
Plugins can be registered at runtime or discovered via entry points.

Example:
    >>> from momapy.plugins import PluginRegistry
    >>> registry = PluginRegistry(entry_point_group="myapp.plugins")
    >>> registry.register("plugin", PluginClass)
"""

from momapy.plugins import registry


PluginRegistry = registry.PluginRegistry
__all__ = ["PluginRegistry"]
