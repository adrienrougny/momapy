"""SBML reader with ReadingContext dataclass."""

import os
import typing
import dataclasses
import collections

import frozendict
import lxml.objectify

from momapy.builder import object_from_builder
from momapy.utils import add_or_replace_element_in_set
from momapy.io.core import Reader
from momapy.io.core import ReaderResult
from momapy.sbml.io.sbml._parsing import get_compartments
from momapy.sbml.io.sbml._parsing import get_modifiers
from momapy.sbml.io.sbml._parsing import get_products
from momapy.sbml.io.sbml._parsing import get_reactants
from momapy.sbml.io.sbml._parsing import get_reactions
from momapy.sbml.io.sbml._parsing import get_species
from momapy.sbml.io.sbml._parsing import make_id_to_element_mapping
from momapy.sbml.io.sbml._model import make_annotations_from_element
from momapy.sbml.io.sbml._model import make_compartment
from momapy.sbml.io.sbml._model import make_empty_model
from momapy.sbml.io.sbml._model import make_modifier_species_reference
from momapy.sbml.io.sbml._model import make_notes_from_element
from momapy.sbml.io.sbml._model import make_reaction
from momapy.sbml.io.sbml._model import make_species
from momapy.sbml.io.sbml._model import make_species_reference


@dataclasses.dataclass
class ReadingContext:
    sbml_model: typing.Any
    model: typing.Any
    sbml_id_to_model_element: dict
    sbml_id_to_sbml_element: dict
    element_to_annotations: dict
    element_to_notes: dict
    map_element_to_ids: dict
    with_annotations: bool
    with_notes: bool


class SBMLReader(Reader):
    @staticmethod
    def _register_model_element(
        model_element,
        collection,
        id_,
        id_to_model_element,
    ):
        model_element = add_or_replace_element_in_set(
            model_element,
            collection,
            func=lambda element, existing_element: element.id_ < existing_element.id_,
        )
        id_to_model_element[id_] = model_element
        return model_element

    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
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
        with_annotations=True,
        with_notes=True,
        **options: typing.Any,
    ) -> ReaderResult:
        sbml_document = lxml.objectify.parse(file_path)
        sbml = sbml_document.getroot()
        obj, annotations, notes = cls._make_main_obj(
            sbml_model=sbml.model,
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
    def _make_main_obj(
        cls,
        sbml_model,
        with_annotations=True,
        with_notes=True,
    ):
        model = make_empty_model(sbml_model)
        sbml_id_to_model_element = {}
        element_to_annotations = collections.defaultdict(set)
        map_element_to_ids = collections.defaultdict(set)
        element_to_notes = collections.defaultdict(set)
        sbml_id_to_sbml_element = make_id_to_element_mapping(sbml_model)
        ctx = ReadingContext(
            sbml_model=sbml_model,
            model=model,
            sbml_id_to_model_element=sbml_id_to_model_element,
            sbml_id_to_sbml_element=sbml_id_to_sbml_element,
            element_to_annotations=element_to_annotations,
            element_to_notes=element_to_notes,
            map_element_to_ids=map_element_to_ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        for sbml_compartment in get_compartments(ctx.sbml_model):
            cls._make_and_add_compartment(ctx, sbml_compartment)
        for sbml_species in get_species(ctx.sbml_model):
            cls._make_and_add_species(ctx, sbml_species)
        for sbml_reaction in get_reactions(ctx.sbml_model):
            cls._make_and_add_reaction(ctx, sbml_reaction)
        obj = object_from_builder(model)
        if with_annotations:
            annotations = make_annotations_from_element(sbml_model)
            element_to_annotations[obj].update(annotations)
        if with_notes:
            notes = make_notes_from_element(sbml_model)
            element_to_notes[obj].update(notes)
        element_to_annotations = frozendict.frozendict(
            {key: frozenset(value) for key, value in element_to_annotations.items()}
        )
        element_to_notes = frozendict.frozendict(
            {key: frozenset(value) for key, value in element_to_notes.items()}
        )
        return (
            obj,
            element_to_annotations,
            element_to_notes,
        )

    @classmethod
    def _make_and_add_compartment(cls, ctx, sbml_compartment):
        model_element = make_compartment(sbml_compartment, ctx.model)
        model_element = object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.compartments,
            sbml_compartment.get("id"),
            ctx.sbml_id_to_model_element,
        )
        ctx.map_element_to_ids[model_element].add(sbml_compartment.get("id"))
        if ctx.with_annotations:
            annotations = make_annotations_from_element(sbml_compartment)
            if annotations:
                ctx.element_to_annotations[model_element].update(annotations)
        if ctx.with_notes:
            notes = make_notes_from_element(sbml_compartment)
            ctx.element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_species(cls, ctx, sbml_species):
        model_element = make_species(
            sbml_species, ctx.model, ctx.sbml_id_to_model_element
        )
        model_element = object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.species,
            sbml_species.get("id"),
            ctx.sbml_id_to_model_element,
        )
        if ctx.with_annotations:
            annotations = make_annotations_from_element(sbml_species)
            if annotations:
                ctx.element_to_annotations[model_element].update(annotations)
        if ctx.with_notes:
            notes = make_notes_from_element(sbml_species)
            ctx.element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reaction(cls, ctx, sbml_reaction):
        model_element = make_reaction(sbml_reaction, ctx.model)
        for sbml_reactant in get_reactants(sbml_reaction):
            cls._make_and_add_reactant(ctx, sbml_reactant, model_element)
        for sbml_product in get_products(sbml_reaction):
            cls._make_and_add_product(ctx, sbml_product, model_element)
        for sbml_modifier in get_modifiers(sbml_reaction):
            cls._make_and_add_modifier(ctx, sbml_modifier, model_element)
        model_element = object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.reactions,
            sbml_reaction.get("id"),
            ctx.sbml_id_to_model_element,
        )
        ctx.map_element_to_ids[model_element].add(sbml_reaction.get("id"))
        if ctx.with_annotations:
            annotations = make_annotations_from_element(sbml_reaction)
            if annotations:
                ctx.element_to_annotations[model_element].update(annotations)
            if ctx.with_notes:
                notes = make_notes_from_element(sbml_reaction)
                ctx.element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reactant(cls, ctx, sbml_species_reference, super_model_element):
        model_element = make_species_reference(
            sbml_species_reference, ctx.model, ctx.sbml_id_to_model_element
        )
        super_model_element.reactants.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_product(cls, ctx, sbml_species_reference, super_model_element):
        model_element = make_species_reference(
            sbml_species_reference, ctx.model, ctx.sbml_id_to_model_element
        )
        super_model_element.products.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_modifier(
        cls, ctx, sbml_modifier_species_reference, super_model_element
    ):
        model_element = make_modifier_species_reference(
            sbml_modifier_species_reference, ctx.model, ctx.sbml_id_to_model_element
        )
        super_model_element.modifiers.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element
