"""Generic plugin registry with lazy loading and entry point support.

This module provides a generic plugin registry that supports:
- Direct registration of plugin classes
- Lazy loading of plugins (import on first access)
- Discovery via entry points for third-party plugins

Example:
    >>> from momapy.plugins import PluginRegistry
    >>> # Create a registry for plugins
    >>> registry = PluginRegistry()
    >>> # Register a plugin class (MyPluginClass must be defined/imported)
    >>> # registry.register("my_plugin", MyPluginClass)
    >>> # Retrieve a registered plugin
    >>> # plugin = registry.get("my_plugin")
"""

import importlib
import typing

T = typing.TypeVar("T")


class PluginRegistry(typing.Generic[T]):
    """A generic plugin registry supporting lazy loading and entry points.

    Supports direct registration, lazy loading, and entry point discovery.

    Example:
        >>> registry = PluginRegistry(entry_point_group="myapp.plugins")
        >>> registry.register("plugin1", PluginClass)
        >>> registry.register_lazy("plugin2", "module.submodule:PluginClass")
        >>> plugin = registry.get("plugin1")  # Returns PluginClass
    """

    def __init__(self, entry_point_group: str | None = None):
        """Initialize the registry.

        Args:
            entry_point_group: Entry point group name for discovering third-party
                plugins (e.g., "momapy.renderers"). If None, entry point
                discovery is disabled.
        """
        self._entry_point_group = entry_point_group
        self._lazy_plugins: dict[str, str] = {}
        self._loaded_plugins: dict[str, T] = {}
        self._entry_points_loaded = False

    def register(self, name: str, plugin: T) -> None:
        """Register a plugin class directly.

        Use for runtime registration or when the class is already imported.

        Args:
            name: Name to register the plugin under.
            plugin: The plugin class.

        Example:
            >>> registry.register("my_plugin", MyPlugin)
        """
        self._loaded_plugins[name] = plugin

    def register_lazy(self, name: str, import_path: str) -> None:
        """Register a plugin for lazy loading.

        The plugin is not imported until first accessed via get().

        Args:
            name: Name to register the plugin under.
            import_path: Import path in format "module.path:ClassName".

        Raises:
            ValueError: If import_path format is invalid.

        Example:
            >>> registry.register_lazy("plugin", "mymodule.plugins:PluginClass")
        """
        if ":" not in import_path:
            raise ValueError(
                f"Invalid import path '{import_path}'. "
                f'Expected format: "module.path:ClassName"'
            )
        self._lazy_plugins[name] = import_path

    def get(self, name: str) -> T | None:
        """Get a plugin by name, loading it if necessary.

        Args:
            name: The plugin name.

        Returns:
            The plugin class, or None if not found.

        Raises:
            ImportError: If the plugin module cannot be imported.

        Example:
            >>> plugin = registry.get("my_plugin")
            >>> plugin is None
            True
        """
        if name in self._loaded_plugins:
            return self._loaded_plugins[name]
        if name in self._lazy_plugins:
            return self._load_lazy_plugin(name)
        if not self._entry_points_loaded:
            self._load_entry_points()
            return self.get(name)
        return None

    def is_available(self, name: str) -> bool:
        """Check if a plugin is available without loading it.

        Args:
            name: The plugin name.

        Returns:
            True if the plugin is registered (lazy or loaded).

        Example:
            >>> registry.is_available("my_plugin")
            False
        """
        if not self._entry_points_loaded:
            self._load_entry_points()
        return name in self._loaded_plugins or name in self._lazy_plugins

    def list_available(self) -> list[str]:
        """List all available plugin names.

        Returns:
            Sorted list of all registered plugin names.

        Example:
            >>> registry.list_available()
            ['plugin1', 'plugin2']
        """
        if not self._entry_points_loaded:
            self._load_entry_points()

        names = set(self._loaded_plugins.keys()) | set(self._lazy_plugins.keys())
        return sorted(names)

    def list_loaded(self) -> list[str]:
        """List plugins that have been loaded into memory.

        Returns:
            Sorted list of loaded plugin names.

        Example:
            >>> registry.list_loaded()
            ['plugin1']
        """
        return sorted(self._loaded_plugins.keys())

    def _load_lazy_plugin(self, name: str) -> T:
        """Load a lazy plugin and cache it.

        Args:
            name: Plugin name. Must exist in _lazy_plugins.

        Returns:
            The loaded plugin class.
        """
        import_path = self._lazy_plugins[name]
        module_path, class_name = import_path.rsplit(":", 1)
        module = importlib.import_module(module_path)
        plugin = getattr(module, class_name)
        self._loaded_plugins[name] = plugin
        del self._lazy_plugins[name]
        return plugin

    def _load_entry_points(self) -> None:
        """Discover and register plugins from entry points.

        Scans entry points for the configured entry_point_group and
        registers them as lazy plugins.
        """
        if self._entry_points_loaded:
            return
        self._entry_points_loaded = True
        if not self._entry_point_group:
            return
        import importlib.metadata

        entry_points = importlib.metadata.entry_points(group=self._entry_point_group)
        for entry_point in entry_points:
            if (
                entry_point.name not in self._lazy_plugins
                and entry_point.name not in self._loaded_plugins
            ):
                self._lazy_plugins[entry_point.name] = entry_point.value
