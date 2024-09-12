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
    exceptions: list[Exception] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ReaderResult(IOResult):
    obj: typing.Any | None = None
    annotations: dict | None = None
    notes: dict | None = None
    file_path: str | None = None


@dataclasses.dataclass
class WriterResult(IOResult):
    obj: typing.Any | None = None
    exceptions: str | None = None
    file_path: str | None = None


def read_file(
    file_path: str,
    reader: str | None = None,
    **options,
) -> ReaderResult:
    """Read and return a map from a file. If no reader is given, will check for an appropriate reader among the registered readers, using the `check_file` method. If there is more than one appropriate reader, will use the first one."""
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
        result = reader_cls.read_file(file_path, **options)
    else:
        raise ValueError(
            f"could not find a suitable registered reader for file '{file_path}'"
        )
    return result


def write_file(
    obj: typing.Any, file_path: str, writer: str, **options
) -> WriterResult:
    """Write a map to a file, using the given writer"""
    writer_cls = None
    writer_cls = writers.get(writer)
    if writer_cls is None:
        raise ValueError(f"no registered writer named '{writer}'")
    result = writer_cls.write(obj, file_path, **options)
    return result


class Reader(abc.ABC):
    """Abstract class for readers"""

    @classmethod
    @abc.abstractmethod
    def read_file(cls, file_path, **options) -> ReaderResult:
        """Read and return a reader result from a file using the reader"""
        pass

    @classmethod
    def check_file(cls, file_path: str) -> bool:
        """Return `true` if the given file is supported by the reader, `false` otherwise"""
        pass


class Writer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def write_file(
        cls,
        obj: typing.Any,
        file_path: str,
        **options,
    ) -> WriterResult:
        """Write an object to a file"""
        pass
