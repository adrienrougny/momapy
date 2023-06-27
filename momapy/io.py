import abc

import momapy.core

readers = {}


def register_reader(name, reader_cls):
    readers[name] = reader_cls


def read(file_path, reader=None, **options):
    reader_cls = None
    if format_ is not None:
        reader_cls = readers.get(reader)
        if reader_cls is None:
            raise ValueError(f"no registered reader named '{reader}'")
    else:
        for candidate_reader_cls in readers.values():
            if reader.check_file(file_path):
                reader_cls = candidate_reader
                break
    if reader_cls is not None:
        map_ = reader_cls.read(file_path, **options)
    else:
        raise ValueError(
            f"could not find a suitable registered reader for file '{file_path}'"
        )
    return map_


class MapReader(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def read(file_path, **options) -> momapy.core.Map | momapy.core.MapBuilder:
        pass

    def check_file(file_path) -> bool:
        pass
