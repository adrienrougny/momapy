"""Classes for reading and writing pickled CellDesigner maps"""

import os
import typing
import pickle

import momapy.core
import momapy.builder
import momapy.geometry
import momapy.positioning
import momapy.io
import momapy.coloring
import momapy.celldesigner.core
import momapy.sbml.core


class CellDesignerPickleReader(momapy.io.Reader):

    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
        with open(file_path, "rb") as f:
            try:
                pickle.load(f)
            except pickle.UnpicklingError:
                return False
            else:
                return True

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model=True,
        with_layout=True,
        with_annotations=True,
        with_notes=True,
    ) -> momapy.io.ReaderResult:

        def _del_key_from_mapping_by_classes(
            mapping, include_classes=None, exclude_classes=None
        ):
            keys_to_delete = []
            if include_classes is None:
                include_classes = []
            if exclude_classes is None:
                exclude_classes = [object]
            for key in mapping:
                if isinstance(key, tuple(exclude_classes)) and not isinstance(
                    key, tuple(include_classes)
                ):
                    keys_to_delete.append(key)
            for key_to_delete in keys_to_delete:
                del mapping[key_to_delete]

        with open(file_path, "rb") as f:
            reader_result = pickle.load(f)
        if not with_annotations:
            reader_result.annotations = None
        if not with_notes:
            reader_result.notes = None
        obj = reader_result.obj
        if return_type == "model":
            obj = obj.model
            for mapping in [
                reader_result.annotations,
                reader_result.notes,
                reader_result.ids,
            ]:
                if mapping is not None:
                    _del_key_from_mapping_by_classes(
                        mapping, include_classes=[momapy.core.ModelElement]
                    )
        elif return_type == "layout":
            obj = obj.layout
            for mapping in [
                reader_result.annotations,
                reader_result.notes,
                reader_result.ids,
            ]:
                if mapping is not None:
                    _del_key_from_mapping_by_classes(
                        mapping, include_classes=[momapy.core.LayoutElement]
                    )
        else:
            if not with_model or not with_layout:
                map_builder = momapy.builder.builder_from_object(obj)
                if not with_model:
                    map_builder.model = None
                    for mapping in [
                        reader_result.annotations,
                        reader_result.notes,
                        reader_result.ids,
                    ]:
                        if mapping is not None:
                            _del_key_from_mapping_by_classes(
                                mapping,
                                exclude_classes=[
                                    momapy.core.ModelLayout,
                                ],
                            )

                if not with_layout:
                    map_builder.layout = None
                    for mapping in [
                        reader_result.annotations,
                        reader_result.notes,
                        reader_result.ids,
                    ]:
                        if mapping is not None:
                            _del_key_from_mapping_by_classes(
                                mapping,
                                exclude_classes=[
                                    momapy.core.LayoutElement,
                                ],
                            )
                map_builder.layout_model_mapping = None
                obj = momapy.builder.object_from_builder(map_builder)
        reader_result.obj = obj
        return reader_result


class CellDesignerPickleWriter(momapy.io.Writer):

    @classmethod
    def write(
        cls,
        obj: momapy.celldesigner.core.CellDesignerMap,
        file_path: str | os.PathLike,
        annotations=None,
        notes=None,
        ids=None,
    ) -> momapy.io.WriterResult:
        reader_result = momapy.io.ReaderResult(
            obj=obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            file_path=file_path,
        )
        with open(file_path, "wb") as f:
            pickle.dump(reader_result, f)
        writer_result = momapy.io.WriterResult(obj=obj, file_path=file_path)
        return writer_result


momapy.io.register_reader("celldesigner_pickle", CellDesignerPickleReader)
momapy.io.register_writer("celldesigner_pickle", CellDesignerPickleWriter)
