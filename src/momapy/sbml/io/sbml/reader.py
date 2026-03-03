"""SBML reader with ReadingContext dataclass."""

import os
import typing
import dataclasses
import collections

import frozendict
import lxml.objectify

import momapy.builder
import momapy.utils
import momapy.io.core
import momapy.sbml.core
import momapy.sbml.io.sbml._parsing
import momapy.sbml.io.sbml._model


@dataclasses.dataclass
class ReadingContext:
    sbml_model: typing.Any
    model: typing.Any
    sbml_id_to_model_element: dict
    sbml_id_to_sbml_element: dict
    map_element_to_annotations: dict
    map_element_to_notes: dict
    map_element_to_ids: dict
    with_annotations: bool
    with_notes: bool


class SBMLReader(momapy.io.core.Reader):

    @staticmethod
    def _register_model_element(
        model_element,
        collection,
        id_,
        id_to_model_element,
    ):
        model_element = momapy.utils.add_or_replace_element_in_set(
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
    ) -> momapy.io.core.ReaderResult:
        sbml_document = lxml.objectify.parse(file_path)
        sbml = sbml_document.getroot()
        obj, annotations, notes, ids = cls._make_main_obj(
            sbml_model=sbml.model,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = momapy.io.core.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
            ids=ids,
        )
        return result

    @classmethod
    def _make_main_obj(
        cls,
        sbml_model,
        with_annotations=True,
        with_notes=True,
    ):
        model = momapy.sbml.io.sbml._model.make_empty_model(sbml_model)
        sbml_id_to_model_element = {}
        map_element_to_annotations = collections.defaultdict(set)
        map_element_to_ids = collections.defaultdict(set)
        map_element_to_notes = collections.defaultdict(set)
        sbml_id_to_sbml_element = momapy.sbml.io.sbml._parsing.make_id_to_element_mapping(
            sbml_model
        )
        ctx = ReadingContext(
            sbml_model=sbml_model,
            model=model,
            sbml_id_to_model_element=sbml_id_to_model_element,
            sbml_id_to_sbml_element=sbml_id_to_sbml_element,
            map_element_to_annotations=map_element_to_annotations,
            map_element_to_notes=map_element_to_notes,
            map_element_to_ids=map_element_to_ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        for sbml_compartment in momapy.sbml.io.sbml._parsing.get_compartments(ctx.sbml_model):
            cls._make_and_add_compartment(ctx, sbml_compartment)
        for sbml_species in momapy.sbml.io.sbml._parsing.get_species(ctx.sbml_model):
            cls._make_and_add_species(ctx, sbml_species)
        for sbml_reaction in momapy.sbml.io.sbml._parsing.get_reactions(ctx.sbml_model):
            cls._make_and_add_reaction(ctx, sbml_reaction)
        obj = momapy.builder.object_from_builder(model)
        if with_annotations:
            annotations = momapy.sbml.io.sbml._model.make_annotations_from_element(sbml_model)
            map_element_to_annotations[obj].update(annotations)
        if with_notes:
            notes = momapy.sbml.io.sbml._model.make_notes(sbml_model)
            map_element_to_notes[obj].update(notes)
        map_element_to_annotations = frozendict.frozendict(
            {key: frozenset(value) for key, value in map_element_to_annotations.items()}
        )
        map_element_to_notes = frozendict.frozendict(
            {key: frozenset(value) for key, value in map_element_to_notes.items()}
        )
        map_element_to_ids = frozendict.frozendict(
            {key: frozenset(value) for key, value in map_element_to_ids.items()}
        )
        return (
            obj,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
        )

    @classmethod
    def _make_and_add_compartment(cls, ctx, sbml_compartment):
        model_element = momapy.sbml.io.sbml._model.make_compartment(sbml_compartment, ctx.model)
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.compartments,
            sbml_compartment.get("id"),
            ctx.sbml_id_to_model_element,
        )
        ctx.map_element_to_ids[model_element].add(sbml_compartment.get("id"))
        if ctx.with_annotations:
            annotations = momapy.sbml.io.sbml._model.make_annotations_from_element(sbml_compartment)
            if annotations:
                ctx.map_element_to_annotations[model_element].update(annotations)
        if ctx.with_notes:
            notes = momapy.sbml.io.sbml._model.make_notes(sbml_compartment)
            ctx.map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_species(cls, ctx, sbml_species):
        model_element = momapy.sbml.io.sbml._model.make_species(sbml_species, ctx.model, ctx.sbml_id_to_model_element)
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.species,
            sbml_species.get("id"),
            ctx.sbml_id_to_model_element,
        )
        if ctx.with_annotations:
            annotations = momapy.sbml.io.sbml._model.make_annotations_from_element(sbml_species)
            if annotations:
                ctx.map_element_to_annotations[model_element].update(annotations)
        if ctx.with_notes:
            notes = momapy.sbml.io.sbml._model.make_notes(sbml_species)
            ctx.map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reaction(cls, ctx, sbml_reaction):
        model_element = momapy.sbml.io.sbml._model.make_reaction(sbml_reaction, ctx.model)
        for sbml_reactant in momapy.sbml.io.sbml._parsing.get_reactants(sbml_reaction):
            cls._make_and_add_reactant(ctx, sbml_reactant, model_element)
        for sbml_product in momapy.sbml.io.sbml._parsing.get_products(sbml_reaction):
            cls._make_and_add_product(ctx, sbml_product, model_element)
        for sbml_modifier in momapy.sbml.io.sbml._parsing.get_modifiers(sbml_reaction):
            cls._make_and_add_modifier(ctx, sbml_modifier, model_element)
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = cls._register_model_element(
            model_element,
            ctx.model.reactions,
            sbml_reaction.get("id"),
            ctx.sbml_id_to_model_element,
        )
        ctx.map_element_to_ids[model_element].add(sbml_reaction.get("id"))
        if ctx.with_annotations:
            annotations = momapy.sbml.io.sbml._model.make_annotations_from_element(sbml_reaction)
            if annotations:
                ctx.map_element_to_annotations[model_element].update(annotations)
            if ctx.with_notes:
                notes = momapy.sbml.io.sbml._model.make_notes(sbml_reaction)
                ctx.map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reactant(cls, ctx, sbml_species_reference, super_model_element):
        model_element = momapy.sbml.io.sbml._model.make_species_reference(sbml_species_reference, ctx.model, ctx.sbml_id_to_model_element)
        super_model_element.reactants.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_product(cls, ctx, sbml_species_reference, super_model_element):
        model_element = momapy.sbml.io.sbml._model.make_species_reference(sbml_species_reference, ctx.model, ctx.sbml_id_to_model_element)
        super_model_element.products.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_modifier(cls, ctx, sbml_modifier_species_reference, super_model_element):
        model_element = momapy.sbml.io.sbml._model.make_modifier_species_reference(sbml_modifier_species_reference, ctx.model, ctx.sbml_id_to_model_element)
        super_model_element.modifiers.add(model_element)
        ctx.sbml_id_to_model_element[model_element.id_] = model_element
        return model_element
