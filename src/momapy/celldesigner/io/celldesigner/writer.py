"""CellDesigner XML writer class.

Model-first approach: iterates model collections in dependency order,
looking up layout elements via layout_model_mapping. All serialization
logic lives in module-level functions in ``_writing``; this module only
provides the ``write`` entry point.
"""

import os
import typing

import lxml.etree

from momapy.io.core import Writer, WriterResult
from momapy.utils import check_parent_dir_exists
from momapy.celldesigner.map import CellDesignerMap
from momapy.celldesigner.model import Complex
from momapy.celldesigner.io.celldesigner._writing_context import (
    CellDesignerWritingContext,
)
from momapy.celldesigner.io.celldesigner._writing import (
    build_make_sbml_element,
    collect_degraded_entries,
    reserve_source_xml_ids,
)


class CellDesignerWriter(Writer):
    """CellDesigner XML writer (model-first approach).

    **Round-trip caveat.** CellDesigner encodes link geometry as anchor
    ids, edit points, angles, and line directions, whereas momapy stores
    resolved coordinates. On write this encoding is re-derived from those
    coordinates (see `compute_cd_angle` and the anchor/edit-point helpers),
    so a read/write round-trip produces *equivalent* link geometry rather
    than the exact encoding found in the source file.
    """

    @classmethod
    def write(
        cls,
        obj: CellDesignerMap,
        file_path: str | os.PathLike,
        element_to_annotations: dict | None = None,
        element_to_notes: dict | None = None,
        source_id_to_model_element: dict | None = None,
        source_id_to_layout_element: dict | None = None,
        source_id_to_annotations: dict | None = None,
        source_id_to_notes: dict | None = None,
        with_annotations: bool = True,
        with_notes: bool = True,
        **options: typing.Any,
    ) -> WriterResult:
        """Write a CellDesigner map to a file.

        Args:
            obj: A CellDesignerMap instance.
            file_path: Output file path.
            element_to_annotations: Annotations dict from reader result.
            element_to_notes: Notes dict from reader result.
            source_id_to_model_element: Optional source ID to model
                element mapping from ReaderResult.
            source_id_to_layout_element: Optional source ID to layout
                element mapping from ReaderResult.
            source_id_to_annotations: Optional per-source-id annotations
                from ReaderResult.
            source_id_to_notes: Optional per-source-id notes from
                ReaderResult.
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.
            options: Additional options (accepted and ignored).

        Returns:
            WriterResult.
        """
        check_parent_dir_exists(file_path)
        if element_to_annotations is None:
            element_to_annotations = {}
        if element_to_notes is None:
            element_to_notes = {}

        subunit_to_complex: dict = {}
        if obj.model is not None:

            def _collect(species) -> None:
                if isinstance(species, Complex):
                    for sub in species.subunits:
                        # Map to top-level ancestor, not immediate parent.
                        # If the parent is itself a subunit, its entry
                        # was already set (parent before children).
                        ancestor = species
                        while id(ancestor) in subunit_to_complex:
                            ancestor = subunit_to_complex[id(ancestor)]
                        subunit_to_complex[id(sub)] = ancestor
                        _collect(sub)

            for species in obj.model.species:
                _collect(species)

        writing_context = CellDesignerWritingContext(
            map_=obj,
            element_to_annotations=element_to_annotations,
            element_to_notes=element_to_notes,
            source_id_to_model_element=source_id_to_model_element,
            source_id_to_layout_element=source_id_to_layout_element,
            source_id_to_annotations=source_id_to_annotations,
            source_id_to_notes=source_id_to_notes,
            with_annotations=with_annotations,
            with_notes=with_notes,
            subunit_to_complex=subunit_to_complex,
        )
        # Phase 1: reserve all grammar-valid source ids before any
        # emission, so a from-scratch id can never steal a source id's
        # name and round-tripped ids are preserved verbatim.
        reserve_source_xml_ids(writing_context)
        if obj.model is not None and obj.layout is not None:
            writing_context.degraded_entries = collect_degraded_entries(writing_context)

        sbml = build_make_sbml_element(writing_context)
        tree = lxml.etree.ElementTree(sbml)
        tree.write(
            file_path,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        return WriterResult(obj=obj, file_path=file_path)
