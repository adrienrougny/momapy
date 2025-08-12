import os
import collections

import frozendict
import lxml.objectify

import momapy.core
import momapy.geometry
import momapy.positioning
import momapy.io
import momapy.coloring
import momapy.sbml.core


class SBMLReader(momapy.io.Reader):
    _CD_NAMESPACE = "http://www.sbml.org/2001/ns/celldesigner"
    _RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    _QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
        (
            "http://biomodels.net/biology-qualifiers/",
            "encodes",
        ): momapy.sbml.core.BQBiol.ENCODES,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasPart",
        ): momapy.sbml.core.BQBiol.HAS_PART,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasProperty",
        ): momapy.sbml.core.BQBiol.HAS_PROPERTY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasVersion",
        ): momapy.sbml.core.BQBiol.HAS_VERSION,
        (
            "http://biomodels.net/biology-qualifiers/",
            "is",
        ): momapy.sbml.core.BQBiol.IS,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isDescribedBy",
        ): momapy.sbml.core.BQBiol.IS_DESCRIBED_BY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isEncodedBy",
        ): momapy.sbml.core.BQBiol.IS_ENCODED_BY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isHomologTo",
        ): momapy.sbml.core.BQBiol.IS_HOMOLOG_TO,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isPartOf",
        ): momapy.sbml.core.BQBiol.IS_PART_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isPropertyOf",
        ): momapy.sbml.core.BQBiol.IS_PROPERTY_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isVersionOf",
        ): momapy.sbml.core.BQBiol.IS_VERSION_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "occursIn",
        ): momapy.sbml.core.BQBiol.OCCURS_IN,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasTaxon",
        ): momapy.sbml.core.BQBiol.HAS_TAXON,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasInstance",
        ): momapy.sbml.core.BQModel.HAS_INSTANCE,
        (
            "http://biomodels.net/model-qualifiers/",
            "is",
        ): momapy.sbml.core.BQModel.IS,
        (
            "http://biomodels.net/model-qualifiers/",
            "isDerivedFrom",
        ): momapy.sbml.core.BQModel.IS_DERIVED_FROM,
        (
            "http://biomodels.net/model-qualifiers/",
            "isDescribedBy",
        ): momapy.sbml.core.BQModel.IS_DESCRIBED_BY,
        (
            "http://biomodels.net/model-qualifiers/",
            "isInstanceOf",
        ): momapy.sbml.core.BQModel.IS_INSTANCE_OF,
    }

    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
        with open(file_path) as f:
            for line in f:
                if "<sbml " in line:
                    return True
        return False

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        with_annotations=True,
        with_notes=True,
    ) -> momapy.io.ReaderResult:
        sbml_document = lxml.objectify.parse(file_path)
        sbml = sbml_document.getroot()
        obj, annotations, notes, ids = cls._make_main_obj_from_sbml_model(
            sbml_model=sbml.model,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = momapy.io.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
            ids=ids,
        )
        return result

    @classmethod
    def _get_prefix_and_name_from_tag(cls, tag):
        prefix, name = tag.split("}")
        return prefix[1:], name

    @classmethod
    def _get_annotation_from_sbml_element(cls, sbml_element):
        return getattr(sbml_element, "annotation", None)

    @classmethod
    def _get_extension_from_sbml_element(cls, sbml_element):
        sbml_annotation = cls._get_annotation_from_sbml_element(sbml_element)
        if sbml_annotation is None:
            return None
        sbml_extension = getattr(
            sbml_element.annotation, f"{{{cls._CD_NAMESPACE}}}extension", None
        )
        return sbml_extension

    @classmethod
    def _get_species_from_sbml_model(cls, sbml_model):
        list_of_species = getattr(sbml_model, "listOfSpecies", None)
        if list_of_species is None:
            return []
        return list(getattr(list_of_species, "species", []))

    @classmethod
    def _get_reactions_from_sbml_model(cls, sbml_model):
        list_of_reactions = getattr(sbml_model, "listOfReactions", None)
        if list_of_reactions is None:
            return []
        return list(getattr(list_of_reactions, "reaction", []))

    @classmethod
    def _get_compartments_from_sbml_model(cls, sbml_model):
        list_of_compartments = getattr(sbml_model, "listOfCompartments", None)
        if list_of_compartments is None:
            return []
        return list(getattr(list_of_compartments, "compartment", []))

    @classmethod
    def _get_reactants_from_sbml_reaction(cls, sbml_reaction):
        list_of_reactants = getattr(sbml_reaction, "listOfReactants", None)
        if list_of_reactants is None:
            return []
        return list(getattr(list_of_reactants, "speciesReference", []))

    @classmethod
    def _get_products_from_sbml_reaction(cls, sbml_reaction):
        list_of_products = getattr(sbml_reaction, "listOfProducts", None)
        if list_of_products is None:
            return []
        return list(getattr(list_of_products, "speciesReference", []))

    @classmethod
    def _get_modifiers_from_sbml_reaction(cls, sbml_reaction):
        list_of_modifiers = getattr(sbml_reaction, "listOfModifiers", None)
        if list_of_modifiers is None:
            return []
        return list(getattr(list_of_modifiers, "modifierSpeciesReference", []))

    @classmethod
    def _get_notes_from_sbml_element(cls, sbml_element):
        return getattr(sbml_element, "notes", None)

    @classmethod
    def _get_rdf_from_sbml_element(cls, sbml_element):
        annotation = cls._get_annotation_from_sbml_element(sbml_element)
        if annotation is None:
            return None
        return getattr(annotation, f"{{{cls._RDF_NAMESPACE}}}RDF", None)

    @classmethod
    def _get_description_from_rdf(cls, rdf):
        return getattr(rdf, "Description", None)

    @classmethod
    def _get_bags_from_bq_element(cls, bq_element):
        return list(getattr(bq_element, f"{{{cls._RDF_NAMESPACE}}}Bag", []))

    @classmethod
    def _get_lis_from_bag(cls, bag):
        return list(getattr(bag, "li", []))

    @classmethod
    def _make_annotations_from_sbml_rdf(cls, sbml_rdf):
        annotations = []
        description = cls._get_description_from_rdf(sbml_rdf)
        if description is not None:
            for bq_element in description.getchildren():
                key = cls._get_prefix_and_name_from_tag(bq_element.tag)
                qualifier = cls._QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(
                    key
                )
                if qualifier is not None:
                    bags = cls._get_bags_from_bq_element(bq_element)
                    for bag in bags:
                        lis = cls._get_lis_from_bag(bag)
                        resources = [
                            li.get(f"{{{cls._RDF_NAMESPACE}}}resource")
                            for li in lis
                        ]
                        annotation = momapy.sbml.core.RDFAnnotation(
                            qualifier=qualifier,
                            resources=frozenset(resources),
                        )
                        annotations.append(annotation)
        return annotations

    @classmethod
    def _make_notes_from_sbml_element(cls, sbml_element):
        sbml_notes = cls._get_notes_from_sbml_element(sbml_element)
        if sbml_notes is not None:
            for child_element in sbml_notes.iterchildren():
                break
            return lxml.etree.tostring(child_element)
        return []

    @classmethod
    def _make_annotations_from_sbml_element(cls, sbml_element):
        sbml_rdf = cls._get_rdf_from_sbml_element(sbml_element)
        if sbml_rdf is not None:
            annotations = cls._make_annotations_from_sbml_rdf(sbml_rdf)
        else:
            annotations = []
        return annotations

    @classmethod
    def _make_sbml_id_to_sbml_element_mapping_from_sbml_model(cls, sbml_model):
        sbml_id_to_sbml_element = {}
        # compartments
        for sbml_compartment in cls._get_compartments_from_sbml_model(
            sbml_model
        ):
            sbml_id_to_sbml_element[sbml_compartment.get("id")] = (
                sbml_compartment
            )
        # species
        for sbml_species in cls._get_species_from_sbml_model(sbml_model):
            sbml_id_to_sbml_element[sbml_species.get("id")] = sbml_species
        return sbml_id_to_sbml_element

    @classmethod
    def _make_model_no_subelements_from_sbml_model(
        cls,
        sbml_element,
    ):
        model = momapy.sbml.core.SBMLModelBuilder()
        return model

    @classmethod
    def _make_main_obj_from_sbml_model(
        cls,
        sbml_model,
        with_annotations=True,
        with_notes=True,
    ):
        model = cls._make_model_no_subelements_from_sbml_model(sbml_model)
        sbml_id_to_model_element = {}
        map_element_to_annotations = collections.defaultdict(set)
        map_element_to_ids = collections.defaultdict(set)
        map_element_to_notes = collections.defaultdict(set)
        sbml_id_to_sbml_element = (
            cls._make_sbml_id_to_sbml_element_mapping_from_sbml_model(
                sbml_model
            )
        )
        # we make and add the  model and layout elements from the cd elements
        # we start with the compartments
        cls._make_and_add_compartments_from_sbml_model(
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
        # we make and add the species
        cls._make_and_add_species_from_sbml_model(
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
        # we make and add the reactions
        cls._make_and_add_reactions_from_sbml_model(
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
        obj = momapy.builder.object_from_builder(model)
        if with_annotations:
            annotations = cls._make_annotations_from_sbml_element(sbml_model)
            map_element_to_annotations[obj].update(annotations)
        if with_notes:
            notes = cls._make_notes_from_sbml_element(sbml_model)
            map_element_to_notes[obj].update(notes)
        map_element_to_annotations = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in map_element_to_annotations.items()
            }
        )
        map_element_to_notes = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in map_element_to_notes.items()
            }
        )
        map_element_to_ids = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in map_element_to_ids.items()
            }
        )
        return (
            obj,
            map_element_to_annotations,
            map_element_to_notes,
            map_element_to_ids,
        )

    @classmethod
    def _make_and_add_compartments_from_sbml_model(
        cls,
        sbml_model,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for sbml_compartment in cls._get_compartments_from_sbml_model(
            sbml_model
        ):
            _ = cls._make_and_add_compartment_from_sbml_compartment(
                sbml_compartment=sbml_compartment,
                model=model,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )

    @classmethod
    def _make_and_add_species_from_sbml_model(
        cls,
        sbml_model,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for sbml_species in cls._get_species_from_sbml_model(sbml_model):
            _ = cls._make_and_add_species_from_sbml_species(
                sbml_species=sbml_species,
                model=model,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )

    @classmethod
    def _make_and_add_reactions_from_sbml_model(
        cls,
        sbml_model,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for sbml_reaction in cls._get_reactions_from_sbml_model(sbml_model):
            _ = cls._make_and_add_reaction_from_sbml_reaction(
                sbml_reaction=sbml_reaction,
                model=model,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )

    @classmethod
    def _make_and_add_compartment_from_sbml_compartment(
        cls,
        sbml_compartment,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        model_element = model.new_element(momapy.sbml.core.Compartment)
        model_element.id_ = sbml_compartment.get("id")
        model_element.name = sbml_compartment.get("name")
        model_element.metaid = sbml_compartment.get("metaid")
        model_element.sbo_term = sbml_compartment.get("sboTerm")
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = momapy.utils.add_or_replace_element_in_set(
            model_element,
            model.compartments,
            func=lambda element, existing_element: element.id_
            < existing_element.id_,
        )
        sbml_id_to_model_element[sbml_compartment.get("id")] = model_element
        map_element_to_ids[model_element].add(sbml_compartment.get("id"))
        if with_annotations:
            annotations = cls._make_annotations_from_sbml_element(
                sbml_compartment
            )
            if annotations:
                map_element_to_annotations[model_element].update(annotations)
        if with_notes:
            notes = cls._make_notes_from_sbml_element(sbml_compartment)
            map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_species_from_sbml_species(
        cls,
        sbml_species,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        model_element = model.new_element(momapy.sbml.core.Species)
        model_element.name = sbml_species.get("name")
        model_element.id_ = sbml_species.get("id")
        model_element.metaid = sbml_species.get("metaid")
        model_element.sbo_term = sbml_species.get("sboTerm")
        sbml_compartment_id = sbml_species.get("compartment")
        if sbml_compartment_id is not None:
            compartment_model_element = sbml_id_to_model_element[
                sbml_compartment_id
            ]
            model_element.compartment = compartment_model_element
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = momapy.utils.add_or_replace_element_in_set(
            model_element,
            model.species,
            func=lambda element, existing_element: element.id_
            < existing_element.id_,
        )
        sbml_id_to_model_element[sbml_species.get("id")] = model_element
        if with_annotations:
            annotations = cls._make_annotations_from_sbml_element(sbml_species)
            if annotations:
                map_element_to_annotations[model_element].update(annotations)
        if with_notes:
            notes = cls._make_notes_from_sbml_element(sbml_species)
            map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reaction_from_sbml_reaction(
        cls,
        sbml_reaction,
        model,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        model_element = model.new_element(momapy.sbml.core.Reaction)
        model_element.id_ = sbml_reaction.get("id")
        model_element.name = sbml_reaction.get("name")
        model_element.sbo_term = sbml_reaction.get("sboTerm")
        model_element.reversible = sbml_reaction.get("reversible") == "true"
        for sbml_reactant in cls._get_reactants_from_sbml_reaction(
            sbml_reaction
        ):
            _ = cls._make_and_add_reactant_from_sbml_species_reference(
                model=model,
                sbml_species_reference=sbml_reactant,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
                super_sbml_element=sbml_reaction,
                super_model_element=model_element,
            )
        for sbml_product in cls._get_products_from_sbml_reaction(
            sbml_reaction
        ):
            _ = cls._make_and_add_product_from_sbml_species_reference(
                model=model,
                sbml_species_reference=sbml_product,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
                super_sbml_element=sbml_reaction,
                super_model_element=model_element,
            )
        for sbml_modifier in cls._get_modifiers_from_sbml_reaction(
            sbml_reaction
        ):
            _ = cls._make_and_add_modifier_from_sbml_modifier_species_reference(
                model=model,
                sbml_modifier_species_reference=sbml_modifier,
                sbml_id_to_model_element=sbml_id_to_model_element,
                sbml_id_to_sbml_element=sbml_id_to_sbml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
                super_sbml_element=sbml_reaction,
                super_model_element=model_element,
            )
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = momapy.utils.add_or_replace_element_in_set(
            model_element,
            model.reactions,
            func=lambda element, existing_element: element.id_
            < existing_element.id_,
        )
        sbml_id_to_model_element[sbml_reaction.get("id")] = model_element
        map_element_to_ids[model_element].add(sbml_reaction.get("id"))
        if with_annotations:
            annotations = cls._make_annotations_from_sbml_element(
                sbml_reaction
            )
            if annotations:
                map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbml_element(sbml_reaction)
                map_element_to_notes[model_element].update(notes)
        return model_element

    @classmethod
    def _make_and_add_reactant_from_sbml_species_reference(
        cls,
        model,
        sbml_species_reference,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_sbml_element,
        super_model_element,
    ):
        model_element = model.new_element(momapy.sbml.core.SpeciesReference)
        sbml_species_id = sbml_species_reference.get("species")
        model_element.id_ = sbml_species_reference.get("metaid")
        sbml_stoichiometry = sbml_species_reference.get("stoichiometry")
        if sbml_stoichiometry is not None:
            model_element.stoichiometry = float(sbml_stoichiometry)
        species_model_element = sbml_id_to_model_element[sbml_species_id]
        model_element.referred_species = species_model_element
        model_element = momapy.builder.object_from_builder(model_element)
        super_model_element.reactants.add(model_element)
        sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_product_from_sbml_species_reference(
        cls,
        model,
        sbml_species_reference,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_sbml_element,
        super_model_element,
    ):
        model_element = model.new_element(momapy.sbml.core.SpeciesReference)
        sbml_species_id = sbml_species_reference.get("species")
        model_element.id_ = sbml_species_reference.get("metaid")
        sbml_stoichiometry = sbml_species_reference.get("stoichiometry")
        if sbml_stoichiometry is not None:
            model_element.stoichiometry = float(sbml_stoichiometry)
        species_model_element = sbml_id_to_model_element[sbml_species_id]
        model_element.referred_species = species_model_element
        model_element = momapy.builder.object_from_builder(model_element)
        super_model_element.products.add(model_element)
        sbml_id_to_model_element[model_element.id_] = model_element
        return model_element

    @classmethod
    def _make_and_add_modifier_from_sbml_modifier_species_reference(
        cls,
        model,
        sbml_modifier_species_reference,
        sbml_id_to_model_element,
        sbml_id_to_sbml_element,
        map_element_to_annotations,
        map_element_to_notes,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_sbml_element,
        super_model_element,
    ):
        model_element = model.new_element(
            momapy.sbml.core.ModifierSpeciesReference
        )
        sbml_species_id = sbml_modifier_species_reference.get("species")
        model_element.id_ = sbml_modifier_species_reference.get("metaid")
        species_model_element = sbml_id_to_model_element[sbml_species_id]
        model_element.referred_species = species_model_element
        model_element = momapy.builder.object_from_builder(model_element)
        super_model_element.modifiers.add(model_element)
        sbml_id_to_model_element[model_element.id_] = model_element
        return model_element


momapy.io.register_reader("sbml", SBMLReader)
