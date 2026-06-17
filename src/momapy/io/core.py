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

from momapy.plugins.core import PluginRegistry
from momapy.utils import FrozenIdentityMultiDict
from momapy.utils import FrozenSurjectionDict


__all__ = [
    "get_reader",
    "get_writer",
    "list_readers",
    "list_writers",
    "read",
    "Reader",
    "reader_registry",
    "ReaderResult",
    "register_lazy_reader",
    "register_lazy_writer",
    "register_reader",
    "register_writer",
    "write",
    "Writer",
    "writer_registry",
    "WriterResult",
]


reader_registry = PluginRegistry(entry_point_group="momapy.readers")
writer_registry = PluginRegistry(entry_point_group="momapy.writers")


def get_reader(name: str) -> type["Reader"]:
    """Get a reader class by name.

    Args:
        name: Reader name (e.g., "sbgnml", "celldesigner").

    Returns:
        Reader class for the specified format.

    Raises:
        ValueError: If no reader with that name exists.
        ImportError: If the reader is registered but its module cannot be
            imported (e.g. a missing optional dependency).
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
        ImportError: If the writer is registered but its module cannot be
            imported (e.g. a missing optional dependency).
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
            (e.g. XML attributes) to the **set** of model elements
            named by that ID.  Only contains IDs that exist verbatim
            in the source file.  One source ID may name several model
            elements — for example a CellDesigner ``species/@id`` can
            point at both the active and inactive variants of the
            same species.  This is a ``Mapping[str, frozenset[ModelElement]]``:
            use ``.get(id_, frozenset())`` to recover the model elements
            named by an ID, or the ``.inverse`` property
            (``id(element) -> frozenset[str]``) to find every source ID
            that named a given model element.
        source_id_to_layout_element: Mapping from source file IDs
            (e.g. XML attributes) to layout elements.  Only contains
            IDs that exist verbatim in the source file.  Unlike
            ``source_id_to_model_element``, this is a
            ``Mapping[str, LayoutElement]``: each source ID names a
            **single** layout element.  Use ``[id_]`` / ``.get(id_)``
            to recover the layout element named by an ID, or the
            ``.inverse`` property — an equality-keyed (not ``id()``-keyed)
            ``LayoutElement -> frozenset[str]`` — to find every source ID
            that named a given layout element.
        source_id_to_annotations: Mapping from source file IDs to the
            RDF/MIRIAM annotations attached to that specific source
            element.  Parallel to ``element_to_annotations`` but
            preserves per-source granularity when several source
            elements deduplicate to a single model element.  Combine
            with ``source_id_to_model_element.inverse`` to recover the
            full set of source-side annotations that merged into a
            given model element.
        source_id_to_notes: Mapping from source file IDs to the free
            text ``<notes>`` blocks attached to that specific source
            element.  Parallel to ``element_to_notes``; same
            per-source semantics as ``source_id_to_annotations``.
        file_path: Path of the file that was read.
    """

    obj: typing.Any | None = None
    element_to_annotations: frozendict.frozendict | None = None
    element_to_notes: frozendict.frozendict | None = None
    id_to_element: frozendict.frozendict | None = None
    source_id_to_model_element: FrozenIdentityMultiDict | None = None
    source_id_to_layout_element: FrozenSurjectionDict | None = None
    source_id_to_annotations: frozendict.frozendict | None = None
    source_id_to_notes: frozendict.frozendict | None = None
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
    **options: typing.Any,
) -> ReaderResult:
    """Read a map file.

    If reader is specified, uses that reader. Otherwise, checks registered
    readers in registration order and uses the first whose check_file method
    accepts the file. Registration order matters: a more specific reader must
    be registered before a more general one it specializes. For example a
    CellDesigner file is also a valid SBML file, so the CellDesigner reader is
    registered (and therefore checked) before the SBML reader.

    Return contract: the shape of `result.obj` is governed by the universal
    `return_type` option, uniformly across every format:

    - `return_type="map"` (the default) returns a `Map`. This is the uniform
      default for all formats; a layout-less format (SBML) returns a `Map`
      with `layout=None` and `layout_model_mapping=None`.
    - `return_type="model"` returns the bare `Model`.
    - `return_type="layout"` returns the `Layout`; a layout-less format (SBML)
      raises `NotImplementedError`.

    Universal options accepted by every reader (with these defaults):
    `return_type="map"`, `with_model=True`, `with_layout=True`,
    `with_annotations=True`, `with_notes=True`. Unknown keyword options are
    accepted and ignored. Some formats accept extra options (for example the
    SBGN-ML reader's `xsep`/`ysep`).

    Args:
        file_path: Path of the file to read.
        reader: Name of registered reader to use (e.g., "sbgnml"). If None,
            auto-detects based on file format.
        options: Additional options passed to the reader (see the universal
            option set above, plus any format-specific options).

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
        for name in reader_registry.list_available_in_registration_order():
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
    **options: typing.Any,
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
    def read(cls, file_path: str | os.PathLike, **options: typing.Any) -> ReaderResult:
        """Read a file and return the result.

        Concrete readers accept the universal option set with these names,
        types, and defaults, plus a trailing `**options` so unknown keywords
        are accepted and ignored:

        - `return_type: Literal["map", "model", "layout"] = "map"` — the shape
          of `result.obj`. `"map"` returns a `Map` (the uniform default for
          every format), `"model"` returns the `Model`, `"layout"` returns the
          `Layout`. A layout-less format (SBML) raises `NotImplementedError`
          for `"layout"` and returns a `Map` with `layout=None` for `"map"`.
        - `with_model: bool = True` — whether to build the model.
        - `with_layout: bool = True` — whether to build the layout (no effect
          on layout-less formats).
        - `with_annotations: bool = True` — whether to read annotations.
        - `with_notes: bool = True` — whether to read notes.

        Args:
            file_path: Path of the file to read.
            options: Reader-specific options (see the universal set above).

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
        **options: typing.Any,
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
