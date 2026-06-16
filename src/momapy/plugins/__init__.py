"""Plugin system for momapy.

Provides a generic plugin registry for extending momapy functionality.
Plugins can be registered at runtime or discovered via entry points.
"""

from momapy.plugins.core import PluginRegistry as PluginRegistry

__all__ = ["PluginRegistry"]
