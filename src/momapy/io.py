"""Base classes and functions for reading and writing maps"""

import os
import dataclasses
import abc
import typing

readers = {}
writers = {}


def register_reader(name: str, reader_cls: typing.Type):
    """Register a reader"""
    readers[name] = reader_cls


def register_writer(name, writer_cls):
    """Register a writer"""
    writers[name] = writer_cls


@dataclasses.dataclass
class IOResult:
    """Base class for I/O results"""

    exceptions: list[Exception] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ReaderResult(IOResult):
    """Base class for reader results"""

    obj: typing.Any | None = None
    annotations: dict | None = None
    notes: dict | None = None
    ids: dict | None = None
    file_path: str | os.PathLike | None = None


@dataclasses.dataclass
class WriterResult(IOResult):
    """Base class for writer results"""

    obj: typing.Any | None = None
    file_path: str | os.PathLike | None = None


def read(
    file_path: str | os.PathLike,
    reader: str | None = None,
    **options,
) -> ReaderResult:
    """Read a map file and return a reader result using the given registered reader. If no reader is given, will check for an appropriate reader among the registered readers, using the `check_file` method of each reader. If there is more than one appropriate reader, will use the first one.

    Args:
        file_path: The path of the file to read
        reader: The registered reader
        options: Options to be passed to the reader

    Returns:
        A reader result

    """
    reader_cls = None
    if reader is not None:
        reader_cls = readers.get(reader)
        if reader_cls is None:
            raise ValueError(f"no registered reader named '{reader}'")
    else:
        for candidate_reader_cls in readers.values():
            if candidate_reader_cls.check_file(file_path):
                reader_cls = candidate_reader_cls
                break
    if reader_cls is not None:
        result = reader_cls.read(file_path, **options)
    else:
        raise ValueError(
            f"could not find a suitable registered reader for file '{file_path}'"
        )
    return result


def write(
    obj: typing.Any,
    file_path: str | os.PathLike,
    writer: str,
    **options,
) -> WriterResult:
    """Write an object to a file and return a writer result using the given registered writer

    Args:
        obj: The object to write
        file_path: The path of the file to write to
        writer: The registered writer
        options: Options to be passed to the writer

    Returns:
        A writer result
    """
    writer_cls = None
    writer_cls = writers.get(writer)
    if writer_cls is None:
        raise ValueError(f"no registered writer named '{writer}'")
    result = writer_cls.write(obj, file_path, **options)
    return result


class Reader(abc.ABC):
    """Base class for readers"""

    @classmethod
    @abc.abstractmethod
    def read(cls, file_path: str | os.PathLike, **options) -> ReaderResult:
        """Read a file and return a reader result using the reader"""
        pass

    @classmethod
    def check_file(cls, file_path: str | os.PathLike) -> bool:
        """Return `true` if the given file is supported by the reader, `false` otherwise"""
        pass


class Writer(abc.ABC):
    """Base class for writers"""

    @classmethod
    @abc.abstractmethod
    def write(
        cls,
        obj: typing.Any,
        file_path: str | os.PathLike,
        **options,
    ) -> WriterResult:
        """Write an object to a file and return a writer result using the writer"""
        pass
