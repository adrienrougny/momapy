"""Base classes and functions for reading and writing maps.

Provides abstract base classes for readers and writers, along with
convenience functions for reading and writing map files.

Example:
    >>> from momapy.io.core import read, write
    >>> result = read("map.sbgn")
    >>> write(result.obj, "output.sbgn", writer="sbgnml")
"""

import os
import dataclasses
import abc
import typing

import frozendict

import momapy.utils


@dataclasses.dataclass
class IOResult:
    """Base class for I/O results.

    Attributes:
        exceptions: List of exceptions that occurred during I/O.
    """

    exceptions: list[Exception] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ReaderResult(IOResult):
    """Result from reading a map file.

    Attributes:
        obj: The read map object (MapElement or None).
        annotations: Annotations associated with the read.
        notes: Notes associated with the read.
        ids: Mapping of IDs between file and loaded objects.
        file_path: Path of the file that was read.
    """

    obj: typing.Any | None = None
    annotations: frozendict.frozendict | None = None
    notes: frozendict.frozendict | None = None
    ids: momapy.utils.FrozenSurjectionDict | None = None
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

    Example:
        >>> from momapy.io.core import read
        >>> result = read("map.sbgn")
        >>> map_obj = result.obj
    """
    import momapy.io

    reader_cls = None
    if reader is not None:
        reader_cls = momapy.io.get_reader(reader)
    else:
        for name in momapy.io.reader_registry.list_available():
            candidate_cls = momapy.io.get_reader(name)
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

    Example:
        >>> from momapy.io.core import write
        >>> write(map_obj, "output.sbgn", writer="sbgnml")
    """
    import momapy.io

    writer_cls = momapy.io.get_writer(writer)
    if writer_cls is None:
        raise ValueError(f"could not find writer '{writer}' in the registry")
    result = writer_cls.write(obj, file_path, **options)
    return result


class Reader(abc.ABC):
    """Abstract base class for map readers.

    Implementations must override read() and check_file() methods.

    Example:
        >>> class MyFormatReader(Reader):
        ...     @classmethod
        ...     def read(cls, file_path, **options):
        ...         # Implementation
        ...         pass
        ...
        ...     @classmethod
        ...     def check_file(cls, file_path):
        ...         return file_path.endswith(".myfmt")
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

    Example:
        >>> class MyFormatWriter(Writer):
        ...     @classmethod
        ...     def write(cls, obj, file_path, **options):
        ...         # Implementation
        ...         pass
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
