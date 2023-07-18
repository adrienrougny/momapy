import abc

import momapy.core

readers = {}
writers = {}


def register_reader(name, reader_cls):
    readers[name] = reader_cls


def register_writer(name, writer_cls):
    writers[name] = writer_cls


def read(file_path, reader=None, **options):
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
        map_ = reader_cls.read(file_path, **options)
    else:
        raise ValueError(
            f"could not find a suitable registered reader for file '{file_path}'"
        )
    return map_


def write(map_, file_path, writer, **options):
    writer_cls = None
    writer_cls = writers.get(writer)
    if writer_cls is None:
        raise ValueError(f"no registered writer named '{writer}'")
    writer_cls.write(map_, file_path, **options)
    return map_


class MapReader(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def read(
        cls, file_path, **options
    ) -> momapy.core.Map | momapy.core.MapBuilder:
        pass

    @classmethod
    def check_file(cls, file_path) -> bool:
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
        pass
