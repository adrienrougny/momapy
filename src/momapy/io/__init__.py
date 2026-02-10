"""IO subpackage for reading and writing maps.

Provides functions and registries for reading and writing molecular maps
in various formats (SBGN-ML, CellDesigner, SBML, etc.).

Example:
    >>> from momapy.io import get_reader, get_writer
    >>> reader = get_reader("sbgnml")
    >>> writer = get_writer("sbgnml")
"""

from __future__ import annotations

import typing

import momapy.plugins.registry

if typing.TYPE_CHECKING:
    import momapy.io.core


reader_registry = momapy.plugins.registry.PluginRegistry(
    entry_point_group="momapy.readers"
)
writer_registry = momapy.plugins.registry.PluginRegistry(
    entry_point_group="momapy.writers"
)


def get_reader(name: str) -> type[momapy.io.core.Reader]:
    """Get a reader class by name.

    Args:
        name: Reader name (e.g., "sbgnml", "celldesigner").

    Returns:
        Reader class for the specified format.

    Raises:
        ValueError: If no reader with that name exists.

    Example:
        >>> from momapy.io import get_reader
        >>> reader = get_reader("sbgnml")
    """
    reader = reader_registry.get(name)
    if reader is None:
        available = reader_registry.list_available()
        raise ValueError(
            f"No reader named '{name}'. Available readers: {', '.join(available)}"
        )
    return reader


def list_readers() -> list[str]:
    """List all available reader names.

    Returns:
        Sorted list of available reader names.

    Example:
        >>> from momapy.io import list_readers
        >>> list_readers()
        ['celldesigner', 'sbgnml', ...]
    """
    return reader_registry.list_available()


def register_reader(name: str, cls: type[momapy.io.core.Reader]) -> None:
    """Register a reader class.

    Args:
        name: Name to register the reader under.
        cls: Reader class (must inherit from Reader).

    Example:
        >>> from momapy.io import register_reader
        >>> register_reader("myformat", MyFormatReader)
    """
    reader_registry.register(name, cls)


def register_lazy_reader(name: str, import_path: str) -> None:
    """Register a reader for lazy loading.

    Args:
        name: Name to register the reader under.
        import_path: Import path in format "module.path:ClassName".

    Example:
        >>> from momapy.io import register_lazy_reader
        >>> register_lazy_reader("myformat", "mymodule.io:MyFormatReader")
    """
    reader_registry.register_lazy(name, import_path)


def get_writer(name: str) -> type[momapy.io.core.Writer]:
    """Get a writer class by name.

    Args:
        name: Writer name (e.g., "sbgnml", "celldesigner-pickle").

    Returns:
        Writer class for the specified format.

    Raises:
        ValueError: If no writer with that name exists.

    Example:
        >>> from momapy.io import get_writer
        >>> writer = get_writer("sbgnml")
    """
    writer = writer_registry.get(name)
    if writer is None:
        available = writer_registry.list_available()
        raise ValueError(
            f"No writer named '{name}'. Available writers: {', '.join(available)}"
        )
    return writer


def list_writers() -> list[str]:
    """List all available writer names.

    Returns:
        Sorted list of available writer names.

    Example:
        >>> from momapy.io import list_writers
        >>> list_writers()
        ['sbgnml', 'sbgn-pickle', ...]
    """
    return writer_registry.list_available()


def register_writer(name: str, cls: type[momapy.io.core.Writer]) -> None:
    """Register a writer class.

    Args:
        name: Name to register the writer under.
        cls: Writer class (must inherit from Writer).

    Example:
        >>> from momapy.io import register_writer
        >>> register_writer("myformat", MyFormatWriter)
    """
    writer_registry.register(name, cls)


def register_lazy_writer(name: str, import_path: str) -> None:
    """Register a writer for lazy loading.

    Args:
        name: Name to register the writer under.
        import_path: Import path in format "module.path:ClassName".

    Example:
        >>> from momapy.io import register_lazy_writer
        >>> register_lazy_writer("myformat", "mymodule.io:MyFormatWriter")
    """
    writer_registry.register_lazy(name, import_path)


for name, import_path in [
    ("sbgnml", "momapy.sbgn.io.sbgnml:SBGNML0_3Reader"),
    ("sbgnml-0.2", "momapy.sbgn.io.sbgnml:SBGNML0_2Reader"),
    ("sbgnml-0.3", "momapy.sbgn.io.sbgnml:SBGNML0_3Reader"),
    ("sbgn-pickle", "momapy.sbgn.io.pickle:SBGNPickleReader"),
    ("celldesigner", "momapy.celldesigner.io.celldesigner:CellDesignerReader"),
    ("celldesigner-pickle", "momapy.celldesigner.io.pickle:CellDesignerPickleReader"),
    ("sbml", "momapy.sbml.io.sbml:SBMLReader"),
]:
    register_lazy_reader(name, import_path)

for name, import_path in [
    ("sbgnml", "momapy.sbgn.io.sbgnml:SBGNML0_3Writer"),
    ("sbgnml-0.3", "momapy.sbgn.io.sbgnml:SBGNML0_3Writer"),
    ("sbgn-pickle", "momapy.sbgn.io.pickle:SBGNPickleWriter"),
    ("celldesigner-pickle", "momapy.celldesigner.io.pickle:CellDesignerPickleWriter"),
]:
    register_lazy_writer(name, import_path)
