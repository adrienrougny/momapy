"""Subpackage for reading and writing."""

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
    """Get a reader class by name"""
    reader = reader_registry.get(name)
    if reader is None:
        available = reader_registry.list_available()
        raise ValueError(
            f"No reader named '{name}'. Available readers: {', '.join(available)}"
        )
    return reader


def list_readers() -> list[str]:
    """List all available reader names."""
    return reader_registry.list_available()


def register_reader(name: str, cls: type[momapy.io.core.Reader]) -> None:
    """Register a reader class."""
    reader_registry.register(name, cls)


def register_lazy_reader(name: str, import_path: str) -> None:
    """Register a reader class."""
    reader_registry.register_lazy(name, import_path)


def get_writer(name: str) -> type[momapy.io.core.Writer]:
    """Get a writer class by name."""
    writer = writer_registry.get(name)
    if writer is None:
        available = writer_registry.list_available()
        raise ValueError(
            f"No writer named '{name}'. Available writers: {', '.join(available)}"
        )
    return writer


def list_writers() -> list[str]:
    """List all available writer names."""
    return writer_registry.list_available()


def register_writer(name: str, cls: type[momapy.io.core.Writer]) -> None:
    """Register a writer class."""
    writer_registry.register(name, cls)


def register_lazy_writer(name: str, import_path: str) -> None:
    """Register a reader class."""
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
