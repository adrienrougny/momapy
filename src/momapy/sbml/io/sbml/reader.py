"""SBML reader.

Reads an SBML file into an `SBMLMap` (model only; SBML has no layout).
Follows the shared I/O conventions: a `reading_context` first argument, an
`SBMLReadingContext` extending `momapy.io.utils.ReadingContext`, and
module-level `make_*` element builders in `_reading_model`.
"""

import os
import typing
import collections
import dataclasses

import frozendict
import lxml.objectify

from momapy.builder import new_builder_object
from momapy.builder import object_from_builder
from momapy.io.core import Reader
from momapy.io.core import ReaderResult
from momapy.io.utils import ReadingContext
from momapy.sbml.map import SBMLMap
from momapy.sbml.model import SBMLModel
from momapy.sbml.io.sbml._reading_parsing import get_compartments
from momapy.sbml.io.sbml._reading_parsing import get_modifiers
from momapy.sbml.io.sbml._reading_parsing import get_products
from momapy.sbml.io.sbml._reading_parsing import get_reactants
from momapy.sbml.io.sbml._reading_parsing import get_reactions
from momapy.sbml.io.sbml._reading_parsing import get_species
from momapy.sbml.io.sbml._reading_parsing import make_id_to_element_mapping
from momapy.sbml.io.sbml._reading_model import make_and_add_annotations_and_notes
from momapy.sbml.io.sbml._reading_model import make_compartment
from momapy.sbml.io.sbml._reading_model import make_modifier_species_reference
from momapy.sbml.io.sbml._reading_model import make_reaction
from momapy.sbml.io.sbml._reading_model import make_species
from momapy.sbml.io.sbml._reading_model import make_species_reference
from momapy.sbml.io.sbml._reading_model import _register_model_element


@dataclasses.dataclass
class SBMLReadingContext(ReadingContext):
    """Reading context for the SBML reader.

    Extends the shared `ReadingContext` with the SBML-specific fields used
    to resolve cross-references while building the model.
    """

    sbml_model: typing.Any = None
    sbml_id_to_model_element: dict = dataclasses.field(default_factory=dict)
    """SBML XML id -> frozen model element, used to resolve compartment and
    species cross-references while building."""
    sbml_id_to_sbml_element: dict = dataclasses.field(default_factory=dict)
    """SBML XML id -> source SBML lxml element."""


class SBMLReader(Reader):
    """Reader for SBML files (model only; no layout)."""

    @classmethod
    def check_file(cls, file_path: str | os.PathLike) -> bool:
        """Return `True` if the file looks like SBML.

        A CellDesigner file is also a valid SBML file and matches here; the
        `read()` dispatcher resolves the ambiguity by trying readers in
        registration order (CellDesigner before SBML).

        Args:
            file_path: Path of the file to check.

        Returns:
            `True` if the file contains an `<sbml ` element, `False`
            otherwise.
        """
        try:
            with open(file_path) as f:
                for line in f:
                    if "<sbml " in line:
                        return True
            return False
        except Exception:
            return False

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
        **options: typing.Any,
    ) -> ReaderResult:
        """Read an SBML file and return a reader result object.

        Args:
            file_path: Path of the SBML file to read.
            return_type: Shape of `result.obj`: `"map"` (default) returns an
                `SBMLMap`, `"model"` returns the bare `SBMLModel`. SBML has no
                layout, so `"layout"` raises `NotImplementedError`.
            with_model: Whether to build the model. When `False` and
                `return_type="map"`, the map's `model` is `None`. Defaults to
                `True`.
            with_layout: Accepted for signature parity with the other readers;
                SBML has no layout, so it has no effect. Defaults to `True`.
            with_annotations: Whether to read annotations. Defaults to `True`.
            with_notes: Whether to read notes. Defaults to `True`.
            options: Additional reader-specific options (ignored).

        Returns:
            A `ReaderResult` whose `obj` is an `SBMLMap` or `SBMLModel`.

        Raises:
            NotImplementedError: If `return_type="layout"` (SBML has no layout).
        """
        sbml_document = lxml.objectify.parse(file_path)
        sbml = sbml_document.getroot()
        obj, annotations, notes = cls._make_main_obj(
            sbml_model=sbml.model,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = ReaderResult(
            obj=obj,
            element_to_notes=notes,
            element_to_annotations=annotations,
            file_path=file_path,
        )
        return result

    @classmethod
    def _make_empty_map(cls, sbml_model):
        return new_builder_object(SBMLMap)

    @classmethod
    def _make_empty_model(cls, sbml_model):
        return new_builder_object(SBMLModel)

    @classmethod
    def _make_main_obj(
        cls,
        sbml_model,
        return_type: typing.Literal["map", "model", "layout"],
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
    ):
        if return_type == "layout":
            raise NotImplementedError(
                "SBML has no layout; return_type='layout' is not supported"
            )
        if return_type == "model" or return_type == "map" and with_model:
            model = cls._make_empty_model(sbml_model)
        else:
            model = None
        reading_context = SBMLReadingContext(
            xml_root=sbml_model,
            model=model,
            sbml_model=sbml_model,
            sbml_id_to_sbml_element=make_id_to_element_mapping(sbml_model),
            element_to_annotations=collections.defaultdict(set),
            element_to_notes=collections.defaultdict(set),
            source_id_to_annotations=collections.defaultdict(set),
            source_id_to_notes=collections.defaultdict(set),
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        if model is not None:
            for sbml_compartment in get_compartments(sbml_model):
                cls._make_and_add_compartment(reading_context, sbml_compartment)
            for sbml_species in get_species(sbml_model):
                cls._make_and_add_species(reading_context, sbml_species)
            for sbml_reaction in get_reactions(sbml_model):
                cls._make_and_add_reaction(reading_context, sbml_reaction)
        if return_type == "model":
            obj = object_from_builder(model)
            make_and_add_annotations_and_notes(reading_context, sbml_model, obj)
        elif return_type == "map":
            map_ = cls._make_empty_map(sbml_model)
            map_.model = model
            obj = object_from_builder(map_)
            make_and_add_annotations_and_notes(reading_context, sbml_model, obj)
        element_to_annotations = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in reading_context.element_to_annotations.items()
            }
        )
        element_to_notes = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in reading_context.element_to_notes.items()
            }
        )
        return (
            obj,
            element_to_annotations,
            element_to_notes,
        )

    @classmethod
    def _make_and_add_compartment(cls, reading_context, sbml_compartment):
        model_element = make_compartment(reading_context, sbml_compartment)
        model_element = object_from_builder(model_element)
        model_element = _register_model_element(
            reading_context,
            model_element,
            reading_context.model.compartments,
            sbml_compartment.get("id"),
        )
        make_and_add_annotations_and_notes(
            reading_context, sbml_compartment, model_element
        )
        return model_element

    @classmethod
    def _make_and_add_species(cls, reading_context, sbml_species):
        model_element = make_species(reading_context, sbml_species)
        model_element = object_from_builder(model_element)
        model_element = _register_model_element(
            reading_context,
            model_element,
            reading_context.model.species,
            sbml_species.get("id"),
        )
        make_and_add_annotations_and_notes(reading_context, sbml_species, model_element)
        return model_element

    @classmethod
    def _make_and_add_reaction(cls, reading_context, sbml_reaction):
        model_element = make_reaction(reading_context, sbml_reaction)
        for sbml_reactant in get_reactants(sbml_reaction):
            cls._make_and_add_reactant(reading_context, sbml_reactant, model_element)
        for sbml_product in get_products(sbml_reaction):
            cls._make_and_add_product(reading_context, sbml_product, model_element)
        for sbml_modifier in get_modifiers(sbml_reaction):
            cls._make_and_add_modifier(reading_context, sbml_modifier, model_element)
        model_element = object_from_builder(model_element)
        model_element = _register_model_element(
            reading_context,
            model_element,
            reading_context.model.reactions,
            sbml_reaction.get("id"),
        )
        make_and_add_annotations_and_notes(
            reading_context, sbml_reaction, model_element
        )
        return model_element

    @classmethod
    def _make_and_add_reactant(
        cls, reading_context, sbml_species_reference, super_model_element
    ):
        model_element = make_species_reference(reading_context, sbml_species_reference)
        super_model_element.reactants.add(model_element)
        reading_context.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_product(
        cls, reading_context, sbml_species_reference, super_model_element
    ):
        model_element = make_species_reference(reading_context, sbml_species_reference)
        super_model_element.products.add(model_element)
        reading_context.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_modifier(
        cls, reading_context, sbml_modifier_species_reference, super_model_element
    ):
        model_element = make_modifier_species_reference(
            reading_context, sbml_modifier_species_reference
        )
        super_model_element.modifiers.add(model_element)
        reading_context.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element
