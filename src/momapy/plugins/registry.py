"""Generic plugin registry with lazy loading and entry point support"""

import importlib
import typing

T = typing.TypeVar("T")


class PluginRegistry(typing.Generic[T]):
    """A generic plugin registry supporting lazy loading and entry points"""

    def __init__(self, entry_point_group: str | None = None):
        """Initialize the registry

        Args:
            entry_point_group: The entry point group name for discovering
                third-party plugins (e.g., "momapy.renderers"). If None,
                entry point discovery is disabled.
        """
        self._entry_point_group = entry_point_group
        self._lazy_plugins: dict[str, str] = {}
        self._loaded_plugins: dict[str, T] = {}
        self._entry_points_loaded = False

    def register(self, name: str, plugin: T) -> None:
        """Register a plugin class directly

        Use this for runtime registration or when the class is already imported

        Args:
            name: The name to register the plugin under
            plugin: The plugin class
        """
        self._loaded_plugins[name] = plugin

    def register_lazy(self, name: str, import_path: str) -> None:
        """Register a plugin for lazy loading

        The plugin won't be imported until first accessed via get().

        Args:
            name: The name to register the plugin under
            import_path: The import path in format "module.path:ClassName"
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
            name: The plugin name

        Returns:
            The plugin class, or None if not found

        Raises:
            ImportError: If the plugin module cannot be imported
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
        """Check if a plugin is available (without loading it)

        Args:
            name: The plugin name

        Returns:
            True if the plugin is registered (lazy or loaded)
        """
        if not self._entry_points_loaded:
            self._load_entry_points()
        return name in self._loaded_plugins or name in self._lazy_plugins

    def list_available(self) -> list[str]:
        """List all available plugin names.

        Returns:
            A sorted list of all registered plugin names
        """
        if not self._entry_points_loaded:
            self._load_entry_points()

        names = set(self._loaded_plugins.keys()) | set(self._lazy_plugins.keys())
        return sorted(names)

    def list_loaded(self) -> list[str]:
        """List plugins that have been loaded into memory.

        Returns:
            A sorted list of loaded plugin names
        """
        return sorted(self._loaded_plugins.keys())

    def _load_lazy_plugin(self, name: str) -> T:
        """Load a lazy plugin and cache it.

        Args:
            name: The plugin name (must exist in _lazy_plugins)

        Returns:
            The loaded plugin class
        """
        import_path = self._lazy_plugins[name]
        module_path, class_name = import_path.rsplit(":", 1)
        module = importlib.import_module(module_path)
        plugin = getattr(module, class_name)
        self._loaded_plugins[name] = plugin
        del self._lazy_plugins[name]
        return plugin

    def _load_entry_points(self) -> None:
        """Discover and register plugins from entry points."""
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
