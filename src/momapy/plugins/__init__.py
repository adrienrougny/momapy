"""Plugin system for momapy"""

from momapy.plugins import registry


PluginRegistry = registry.PluginRegistry
__all__ = ["PluginRegistry"]
