import abc
import typing

import momapy.core

_readers = {}
_writers = {}


def register_reader(name: str, reader_cls: typing.Type):
    """Register a reader"""
    _readers[name] = reader_cls


def register_writer(name, writer_cls):
    """Register a writer"""
    _writers[name] = writer_cls


def read(
    file_path: str, reader: str | None = None, **options
) -> momapy.core.Map:
    """Read and return a map from a file. If no reader is given, will check for an appropriate reader among the registered readers, using the `check_file` method. If there is more than one appropriate reader, will use the first one."""
    reader_cls = None
    if reader is not None:
        reader_cls = _readers.get(reader)
        if reader_cls is None:
            raise ValueError(f"no registered reader named '{reader}'")
    else:
        for candidate_reader_cls in _readers.values():
            if candidate_reader_cls.check_file(file_path):
                reader_cls = candidate_reader_cls
                break
    if reader_cls is not None:
        map_ = reader_cls.read(file_path, **options)
    else:
        raise ValueError(
            f"could not find a suitable registered reader for file '{file_path}'"
        )
    return map_


def write(map_: momapy.core.Map, file_path: str, writer: str, **options):
    """Write a map to a file, using the given writer"""
    writer_cls = None
    writer_cls = _writers.get(writer)
    if writer_cls is None:
        raise ValueError(f"no registered writer named '{writer}'")
    writer_cls.write(map_, file_path, **options)


class MapReader(abc.ABC):
    """Abstract class for map reader objects"""

    @classmethod
    @abc.abstractmethod
    def read(cls, file_path, **options) -> momapy.core.Map:
        """Read and return a map from a file using the reader"""
        pass

    @classmethod
    def check_file(cls, file_path: str) -> bool:
        """Return `true` if the given file is supported by the reader, `false` otherwise"""
        pass


class MapWriter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def write(
        cls,
        map_: momapy.core.Map | momapy.core.MapBuilder,
        file_path,
        **options,
    ):
        """Write a map to a file"""
        pass
