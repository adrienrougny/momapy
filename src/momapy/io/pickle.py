"""Pickle-based reader and writer.

Pickle is format-agnostic: the class of the pickled `obj` (SBGN map,
CellDesigner map, ...) survives the round-trip unchanged, so one pair
of classes handles all formats. Registered under the single name
`"pickle"` in `momapy.io`.
"""

import os
import pickle
import typing

import momapy.builder
import momapy.core.elements
import momapy.core.map
import momapy.io.core


def _filter_mapping_by_classes(
    mapping, include_classes=None, exclude_classes=None
):
    """Return a new mapping of the same type with filtered keys.

    A key is kept unless it is an instance of any class in
    ``exclude_classes`` without also being an instance of any class in
    ``include_classes``. Non-mutating: the original mapping (which may
    be a `frozendict`) is not touched.
    """
    if include_classes is None:
        include_classes = []
    if exclude_classes is None:
        exclude_classes = [object]
    include = tuple(include_classes)
    exclude = tuple(exclude_classes)
    kept = {
        key: value
        for key, value in mapping.items()
        if not (isinstance(key, exclude) and not isinstance(key, include))
    }
    return type(mapping)(kept)


def _filter_annotation_mappings(
    reader_result, include_classes=None, exclude_classes=None
):
    """Rebuild `element_to_annotations` / `element_to_notes` filtered."""
    if reader_result.element_to_annotations is not None:
        reader_result.element_to_annotations = _filter_mapping_by_classes(
            reader_result.element_to_annotations,
            include_classes=include_classes,
            exclude_classes=exclude_classes,
        )
    if reader_result.element_to_notes is not None:
        reader_result.element_to_notes = _filter_mapping_by_classes(
            reader_result.element_to_notes,
            include_classes=include_classes,
            exclude_classes=exclude_classes,
        )


class PickleReader(momapy.io.core.Reader):
    """Reader for pickled maps."""

    @classmethod
    def check_file(cls, file_path: str | os.PathLike) -> bool:
        """Return True if `file_path` contains a valid pickle stream."""
        with open(file_path, "rb") as f:
            try:
                pickle.load(f)
            except Exception:
                return False
            return True

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
    ) -> momapy.io.core.ReaderResult:
        """Load a pickled `ReaderResult` and project it per the flags."""
        with open(file_path, "rb") as f:
            reader_result = pickle.load(f)
        if not with_annotations:
            reader_result.element_to_annotations = None
        if not with_notes:
            reader_result.element_to_notes = None
        obj = reader_result.obj
        if return_type == "model":
            obj = obj.model
            _filter_annotation_mappings(
                reader_result,
                include_classes=[momapy.core.elements.ModelElement],
            )
        elif return_type == "layout":
            obj = obj.layout
            _filter_annotation_mappings(
                reader_result,
                include_classes=[momapy.core.elements.LayoutElement],
            )
        elif not with_model or not with_layout:
            map_builder = momapy.builder.builder_from_object(obj)
            if not with_model:
                map_builder.model = None
                _filter_annotation_mappings(
                    reader_result,
                    exclude_classes=[momapy.core.elements.ModelElement],
                )
            if not with_layout:
                map_builder.layout = None
                _filter_annotation_mappings(
                    reader_result,
                    exclude_classes=[momapy.core.elements.LayoutElement],
                )
            map_builder.layout_model_mapping = None
            obj = momapy.builder.object_from_builder(map_builder)
        reader_result.obj = obj
        return reader_result


class PickleWriter(momapy.io.core.Writer):
    """Writer for pickled maps."""

    @classmethod
    def write(
        cls,
        obj: momapy.core.map.Map,
        file_path: str | os.PathLike,
        element_to_annotations=None,
        element_to_notes=None,
        id_to_element=None,
        source_id_to_model_element=None,
        source_id_to_layout_element=None,
    ) -> momapy.io.core.WriterResult:
        """Pickle a `ReaderResult` holding `obj` and its side-tables."""
        reader_result = momapy.io.core.ReaderResult(
            obj=obj,
            element_to_annotations=element_to_annotations,
            element_to_notes=element_to_notes,
            id_to_element=id_to_element,
            source_id_to_model_element=source_id_to_model_element,
            source_id_to_layout_element=source_id_to_layout_element,
            file_path=file_path,
        )
        with open(file_path, "wb") as f:
            pickle.dump(reader_result, f)
        return momapy.io.core.WriterResult(obj=obj, file_path=file_path)
