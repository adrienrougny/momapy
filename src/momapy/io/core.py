"""Base classes and functions for reading and writing maps.

Provides abstract base classes for readers and writers, along with
convenience functions for reading and writing map files.

Examples:
    ```python
    from momapy.io.core import read, write
    result = read("map.sbgn")
    write(result.obj, "output.sbgn", writer="sbgnml")
    ```
"""

import os
import dataclasses
import abc
import typing

import frozendict

import momapy.plugins.core
import momapy.utils


reader_registry = momapy.plugins.core.PluginRegistry(entry_point_group="momapy.readers")
writer_registry = momapy.plugins.core.PluginRegistry(entry_point_group="momapy.writers")


def get_reader(name: str) -> type["Reader"]:
    """Get a reader class by name.

    Args:
        name: Reader name (e.g., "sbgnml", "celldesigner").

    Returns:
        Reader class for the specified format.

    Raises:
        ValueError: If no reader with that name exists.
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
    """
    return reader_registry.list_available()


def register_reader(name: str, cls: type["Reader"]) -> None:
    """Register a reader class.

    Args:
        name: Name to register the reader under.
        cls: Reader class (must inherit from Reader).
    """
    reader_registry.register(name, cls)


def register_lazy_reader(name: str, import_path: str) -> None:
    """Register a reader for lazy loading.

    Args:
        name: Name to register the reader under.
        import_path: Import path in format "module.path:ClassName".
    """
    reader_registry.register_lazy(name, import_path)


def get_writer(name: str) -> type["Writer"]:
    """Get a writer class by name.

    Args:
        name: Writer name (e.g., "sbgnml", "pickle").

    Returns:
        Writer class for the specified format.

    Raises:
        ValueError: If no writer with that name exists.
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
    """
    return writer_registry.list_available()


def register_writer(name: str, cls: type["Writer"]) -> None:
    """Register a writer class.

    Args:
        name: Name to register the writer under.
        cls: Writer class (must inherit from Writer).
    """
    writer_registry.register(name, cls)


def register_lazy_writer(name: str, import_path: str) -> None:
    """Register a writer for lazy loading.

    Args:
        name: Name to register the writer under.
        import_path: Import path in format "module.path:ClassName".
    """
    writer_registry.register_lazy(name, import_path)


@dataclasses.dataclass
class IOResult:
    """Base class for I/O results."""


@dataclasses.dataclass
class ReaderResult(IOResult):
    """Result from reading a map file.

    Attributes:
        obj: The read map object (MapElement or None).
        element_to_annotations: Mapping from map elements to their
            annotations.
        element_to_notes: Mapping from map elements to their notes.
        id_to_element: Mapping from momapy element IDs to elements.
            Contains all model and layout elements regardless of
            source ID provenance.
        source_id_to_model_element: Mapping from source file IDs
            (e.g. XML attributes) to model elements.  Only contains
            IDs that exist verbatim in the source file.  Writers can
            use the ``.inverse`` property to recover original source
            IDs for roundtrip fidelity.
        source_id_to_layout_element: Mapping from source file IDs
            (e.g. XML attributes) to layout elements.  Same
            constraints as ``source_id_to_model_element``.
        file_path: Path of the file that was read.
    """

    obj: typing.Any | None = None
    element_to_annotations: frozendict.frozendict | None = None
    element_to_notes: frozendict.frozendict | None = None
    id_to_element: frozendict.frozendict | None = None
    source_id_to_model_element: momapy.utils.FrozenSurjectionDict | None = None
    source_id_to_layout_element: momapy.utils.FrozenSurjectionDict | None = None
    file_path: str | os.PathLike | None = None


@dataclasses.dataclass
class WriterResult(IOResult):
    """Result from writing a map file.

    Attributes:
        obj: The written object.
        file_path: Path of the file that was written.
    """

    obj: typing.Any | None = None
    file_path: str | os.PathLike | None = None


def read(
    file_path: str | os.PathLike,
    reader: str | None = None,
    **options,
) -> ReaderResult:
    """Read a map file.

    If reader is specified, uses that reader. Otherwise, checks all registered
    readers to find one that supports the file format using their check_file
    method. Uses the first matching reader found.

    Args:
        file_path: Path of the file to read.
        reader: Name of registered reader to use (e.g., "sbgnml"). If None,
            auto-detects based on file format.
        options: Additional options passed to the reader.

    Returns:
        ReaderResult containing the read object and metadata.

    Raises:
        ValueError: If no suitable reader is found.

    Examples:
        ```python
        from momapy.io.core import read
        result = read("map.sbgn")
        map_obj = result.obj
        ```
    """
    if reader is not None:
        reader_cls = get_reader(reader)
    else:
        reader_cls = None
        for name in reader_registry.list_available():
            candidate_cls = get_reader(name)
            if candidate_cls.check_file(file_path):
                reader_cls = candidate_cls
                break
        if reader_cls is None:
            raise ValueError(
                f"could not find a suitable registered reader for file '{file_path}'"
            )
    result = reader_cls.read(file_path, **options)
    return result


def write(
    obj: typing.Any,
    file_path: str | os.PathLike,
    writer: str,
    **options,
) -> WriterResult:
    """Write an object to a file.

    Args:
        obj: Object to write (typically a MapElement).
        file_path: Path of the file to write to.
        writer: Name of registered writer to use (e.g., "sbgnml").
        options: Additional options passed to the writer.

    Returns:
        WriterResult containing the written object and metadata.

    Raises:
        ValueError: If the writer is not found.

    Examples:
        ```python
        from momapy.io.core import write
        write(map_obj, "output.sbgn", writer="sbgnml")
        ```
    """
    writer_cls = get_writer(writer)
    result = writer_cls.write(obj, file_path, **options)
    return result


class Reader(abc.ABC):
    """Abstract base class for map readers.

    Implementations must override read() and check_file() methods.

    Examples:
        ```python
        class MyFormatReader(Reader):
            @classmethod
            def read(cls, file_path, **options):

                # Implementation
                pass

            @classmethod
            def check_file(cls, file_path):
                return file_path.endswith(".myfmt")
        ```
    """

    @classmethod
    @abc.abstractmethod
    def read(cls, file_path: str | os.PathLike, **options) -> ReaderResult:
        """Read a file and return the result.

        Args:
            file_path: Path of the file to read.
            options: Reader-specific options.

        Returns:
            ReaderResult containing the read object.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def check_file(cls, file_path: str | os.PathLike) -> bool:
        """Check if this reader supports the given file.

        Args:
            file_path: Path of the file to check.

        Returns:
            True if the file is supported by this reader.
        """
        pass


class Writer(abc.ABC):
    """Abstract base class for map writers.

    Implementations must override the write() method.

    Examples:
        ```python
        class MyFormatWriter(Writer):
            @classmethod
            def write(cls, obj, file_path, **options):

                # Implementation
                pass
        ```
    """

    @classmethod
    @abc.abstractmethod
    def write(
        cls,
        obj: typing.Any,
        file_path: str | os.PathLike,
        **options,
    ) -> WriterResult:
        """Write an object to a file.

        Args:
            obj: Object to write.
            file_path: Path of the file to write to.
            options: Writer-specific options.

        Returns:
            WriterResult containing the written object.
        """
        pass
