"""SBGN-ML reader classes."""

import os
import abc
import collections
import dataclasses
import typing

import frozendict
import lxml.objectify
import lxml.etree

import momapy.geometry
import momapy.utils
import momapy.core
import momapy.core.mapping
import momapy.core.elements
import momapy.core.layout
import momapy.io.core
import momapy.io.utils
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.drawing
import momapy.styling
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbml.core
import momapy.sbgn.io.sbgnml._reading_classification
import momapy.sbgn.io.sbgnml._reading_parsing
import momapy.sbgn.io.sbgnml._reading_model
import momapy.sbgn.io.sbgnml._reading_layout


@dataclasses.dataclass
class ReadingContext(momapy.io.utils.ReadingContext):
    """SBGN-specific reading context."""

    sbgnml_compartments: list = dataclasses.field(default_factory=list)
    sbgnml_entity_pools: list = dataclasses.field(default_factory=list)
    sbgnml_logical_operators: list = dataclasses.field(default_factory=list)
    sbgnml_stoichiometric_processes: list = dataclasses.field(
        default_factory=list
    )
    sbgnml_phenotypes: list = dataclasses.field(default_factory=list)
    sbgnml_submaps: list = dataclasses.field(default_factory=list)
    sbgnml_activities: list = dataclasses.field(default_factory=list)
    sbgnml_modulations: list = dataclasses.field(default_factory=list)
    sbgnml_tags: list = dataclasses.field(default_factory=list)
    sbgnml_glyph_id_to_sbgnml_arcs: dict = dataclasses.field(
        default_factory=dict
    )


class _SBGNMLReader(momapy.io.core.Reader):

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
        with_styles: bool = True,
        xsep: float = 0,
        ysep: float = 0,
    ) -> momapy.io.core.ReaderResult:
        """Read an SBGN-ML file and return a reader result object"""

        sbgnml_document = lxml.objectify.parse(file_path)
        sbgnml_sbgn = sbgnml_document.getroot()
        obj, annotations, notes = cls._make_main_obj(
            sbgnml_map=sbgnml_sbgn.map,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
            xsep=xsep,
            ysep=ysep,
        )
        result = momapy.io.core.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
        )
        return result

    @classmethod
    @abc.abstractmethod
    def _get_map_key(cls, sbgnml_map):
        pass

    @classmethod
    def _parse_sbgnml_map(cls, reading_context):
        """Classify glyphs and arcs from the XML root into the reading context."""
        sbgnml_map = reading_context.xml_root
        map_key = reading_context.map_key
        reading_context.sbgnml_glyph_id_to_sbgnml_arcs = (
            collections.defaultdict(list)
        )
        module = momapy.sbgn.io.sbgnml._reading_classification.get_module(map_key)
        for sbgnml_glyph in momapy.sbgn.io.sbgnml._reading_parsing.get_glyphs(sbgnml_map):
            reading_context.xml_id_to_xml_element[sbgnml_glyph.get("id")] = sbgnml_glyph
            key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(sbgnml_glyph, map_key)
            model_element_cls, _ = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.EntityPool):
                reading_context.sbgnml_entity_pools.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                module.Compartment,
            ):
                reading_context.sbgnml_compartments.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                module.LogicalOperator,
            ):
                reading_context.sbgnml_logical_operators.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                module.Submap,
            ):
                reading_context.sbgnml_submaps.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.StoichiometricProcess):
                reading_context.sbgnml_stoichiometric_processes.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.Phenotype):
                reading_context.sbgnml_phenotypes.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.af.Activity):
                reading_context.sbgnml_activities.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.Tag):
                reading_context.sbgnml_tags.append(sbgnml_glyph)
            for (
                sbgnml_subglyph
            ) in momapy.sbgn.io.sbgnml._reading_parsing.get_glyphs_recursively(sbgnml_glyph):
                reading_context.xml_id_to_xml_element[sbgnml_subglyph.get("id")] = sbgnml_subglyph
            for sbgnml_port in momapy.sbgn.io.sbgnml._reading_parsing.get_ports(sbgnml_glyph):
                reading_context.xml_id_to_xml_element[sbgnml_port.get("id")] = sbgnml_glyph
        for sbgnml_arc in momapy.sbgn.io.sbgnml._reading_parsing.get_arcs(sbgnml_map):
            reading_context.xml_id_to_xml_element[sbgnml_arc.get("id")] = sbgnml_arc
            sbgnml_source = reading_context.xml_id_to_xml_element[sbgnml_arc.get("source")]
            sbgnml_target = reading_context.xml_id_to_xml_element[sbgnml_arc.get("target")]
            reading_context.sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_source.get("id")].append(sbgnml_arc)
            reading_context.sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_target.get("id")].append(sbgnml_arc)
            key = momapy.sbgn.io.sbgnml._reading_classification.get_arc_key(sbgnml_arc, map_key)
            model_element_cls, _ = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls,
                (momapy.sbgn.pd.Modulation, momapy.sbgn.af.Influence),
            ):
                reading_context.sbgnml_modulations.append(sbgnml_arc)
            for sbgnml_subglyph in momapy.sbgn.io.sbgnml._reading_parsing.get_glyphs(
                sbgnml_arc
            ):
                reading_context.xml_id_to_xml_element[sbgnml_subglyph.get("id")] = sbgnml_subglyph

    @classmethod
    def _make_empty_map(cls, sbgnml_map):
        key = cls._get_map_key(sbgnml_map)
        map_cls, _, _ = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
        if map_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(map_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_empty_model(
        cls,
        sbgnml_map,
    ):
        key = cls._get_map_key(sbgnml_map)
        _, model_cls, _ = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
        if model_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(model_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_empty_layout(cls, sbgnml_map):
        key = cls._get_map_key(sbgnml_map)
        _, _, layout_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
        if layout_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(layout_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_main_obj(
        cls,
        sbgnml_map,
        return_type: typing.Literal["map", "model", "layout"],
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
        with_styles: bool = True,
        xsep: float = 0,
        ysep: float = 0,
    ):
        if return_type == "model" or return_type == "map" and with_model:
            model = cls._make_empty_model(sbgnml_map)
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = cls._make_empty_layout(sbgnml_map)
        else:
            layout = None
        if model is not None or layout is not None:
            if model is not None and layout is not None:
                layout_model_mapping = momapy.core.mapping.LayoutModelMappingBuilder()
            else:
                layout_model_mapping = None
            reading_context = ReadingContext(
                xml_root=sbgnml_map,
                map_key=cls._get_map_key(sbgnml_map),
                model=model,
                layout=layout,
                xml_id_to_model_element=momapy.utils.IdentitySurjectionDict(),
                xml_id_to_layout_element={},
                map_element_to_annotations=collections.defaultdict(set),
                map_element_to_notes=collections.defaultdict(set),
                layout_model_mapping=layout_model_mapping,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # Classify glyphs and arcs into the reading context in one pass.
            cls._parse_sbgnml_map(reading_context)
            # We make model and layout elements from glyphs and arcs; when an arc or
            # a glyph references another sbgnml element, we make the model and
            # layout elements corresponding to that sbgnml element in most cases,
            # and add them to their super model or super layout element accordingly.
            # We make glyphs compartments first as they have to be in the background
            for sbgnml_compartment in reading_context.sbgnml_compartments:
                cls._make_and_add_compartment(
                    reading_context=reading_context,
                    sbgnml_compartment=sbgnml_compartment,
                )
            for sbgnml_entity_pool in reading_context.sbgnml_entity_pools:
                cls._make_and_add_entity_pool(
                    reading_context=reading_context,
                    sbgnml_entity_pool=sbgnml_entity_pool,
                )
            for sbgnml_activity in reading_context.sbgnml_activities:
                cls._make_and_add_activity(
                    reading_context=reading_context,
                    sbgnml_activity=sbgnml_activity,
                )
            for sbgnml_logical_operator in reading_context.sbgnml_logical_operators:
                cls._make_and_add_logical_operator(
                    reading_context=reading_context,
                    sbgnml_logical_operator=sbgnml_logical_operator,
                )
            for sbgnml_submap in reading_context.sbgnml_submaps:
                cls._make_and_add_submap(
                    reading_context=reading_context,
                    sbgnml_submap=sbgnml_submap,
                )
            for sbgnml_phenotype in reading_context.sbgnml_phenotypes:
                cls._make_and_add_phenotype(
                    reading_context=reading_context,
                    sbgnml_phenotype=sbgnml_phenotype,
                )
            for sbgnml_tag in reading_context.sbgnml_tags:
                cls._make_and_add_tag(
                    reading_context=reading_context,
                    sbgnml_tag=sbgnml_tag,
                )
            for sbgnml_process in reading_context.sbgnml_stoichiometric_processes:
                cls._make_and_add_stoichiometric_process(
                    reading_context=reading_context,
                    sbgnml_process=sbgnml_process,
                )
            for sbgnml_modulation in reading_context.sbgnml_modulations:
                cls._make_and_add_modulation(
                    reading_context=reading_context,
                    sbgnml_modulation=sbgnml_modulation,
                )
            # Fix stale references in layout_model_mapping from
            # local variables captured before dedup events.
            if reading_context.model_element_remap and reading_context.layout_model_mapping is not None:
                momapy.io.utils.apply_remap_to_layout_model_mapping(reading_context)
            if layout is not None:
                sbgnml_bbox = getattr(sbgnml_map, "bbox", None)
                if sbgnml_bbox is not None:
                    momapy.sbgn.io.sbgnml._reading_layout.set_position_and_size(
                        layout, sbgnml_map
                    )
                else:
                    momapy.positioning.set_fit(
                        layout, layout.layout_elements, xsep=xsep, ysep=ysep
                    )
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
            # we add the annotations and notes from the map to the model
            momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                reading_context,
                sbgnml_map,
                obj,
            )
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = cls._make_empty_map(sbgnml_map)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = reading_context.layout_model_mapping
            obj = momapy.builder.object_from_builder(map_)
            momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                reading_context,
                sbgnml_map,
                obj,
            )
        map_element_to_annotations = frozendict.frozendict(
            {
                key: frozenset(value)
                for key, value in reading_context.map_element_to_annotations.items()
            }
        )
        map_element_to_notes = frozendict.frozendict(
            {key: frozenset(value) for key, value in reading_context.map_element_to_notes.items()}
        )
        return obj, map_element_to_annotations, map_element_to_notes

    @classmethod
    def _make_and_add_compartment(
        cls,
        reading_context,
        sbgnml_compartment,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_compartment(
                reading_context, sbgnml_compartment
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_compartment(
                reading_context, sbgnml_compartment
            )
            auxiliary_units_map_elements = []
            for sbgnml_unit_of_information in (
                momapy.sbgn.io.sbgnml._reading_parsing.get_units_of_information(
                    sbgnml_compartment
                )
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information(
                    reading_context=reading_context,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model_element is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout_element is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model_element is not None and layout_element is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.compartments,
                    sbgnml_compartment.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context, sbgnml_compartment, model_element
                )
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    sbgnml_compartment.get("id")
                ] = layout_element
            if model_element is not None and layout_element is not None:
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_entity_pool(
        cls,
        reading_context,
        sbgnml_entity_pool,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            model_element, layout_element = cls._make_entity_pool_or_subunit(
                reading_context=reading_context,
                sbgnml_entity_pool_or_subunit=sbgnml_entity_pool,
                super_model_element=None,
                super_layout_element=None,
            )
            if model_element is not None:
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.entity_pools,
                    sbgnml_entity_pool.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context, sbgnml_entity_pool, model_element
                )
            if layout_element is not None:
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    sbgnml_entity_pool.get("id")
                ] = layout_element
            if model_element is not None and layout_element is not None:
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_entity_pool_or_subunit(
        cls,
        reading_context,
        sbgnml_entity_pool_or_subunit,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            is_subunit = (
                super_model_element is not None or super_layout_element is not None
            )
            if is_subunit:
                key = momapy.sbgn.io.sbgnml._reading_classification.get_subglyph_key(
                    sbgnml_entity_pool_or_subunit, reading_context.map_key
                )
            else:
                key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(sbgnml_entity_pool_or_subunit, reading_context.map_key)
            model_element_cls, layout_element_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            model_element = (
                momapy.sbgn.io.sbgnml._reading_model.make_entity_pool_or_subunit(
                    reading_context, sbgnml_entity_pool_or_subunit, model_element_cls
                )
            )
            layout_element = (
                momapy.sbgn.io.sbgnml._reading_layout.make_entity_pool_or_subunit(
                    reading_context, sbgnml_entity_pool_or_subunit, layout_element_cls
                )
            )
            auxiliary_units_map_elements = []
            n_undefined_state_variables = 0
            for (
                sbgnml_state_variable
            ) in momapy.sbgn.io.sbgnml._reading_parsing.get_state_variables(
                sbgnml_entity_pool_or_subunit
            ):
                if momapy.sbgn.io.sbgnml._reading_parsing.has_undefined_variable(
                    sbgnml_state_variable
                ):
                    n_undefined_state_variables += 1
                    order = n_undefined_state_variables
                else:
                    order = None
                state_variable_model_element, state_variable_layout_element = (
                    cls._make_state_variable(
                        reading_context=reading_context,
                        sbgnml_state_variable=sbgnml_state_variable,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        order=order,
                    )
                )
                if model_element is not None:
                    model_element.state_variables.add(state_variable_model_element)
                if layout_element is not None:
                    layout_element.layout_elements.append(state_variable_layout_element)
                if model_element is not None and layout_element is not None:
                    auxiliary_units_map_elements.append(
                        (
                            state_variable_model_element,
                            state_variable_layout_element,
                        )
                    )
            for (
                sbgnml_unit_of_information
            ) in momapy.sbgn.io.sbgnml._reading_parsing.get_units_of_information(
                sbgnml_entity_pool_or_subunit
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information(
                    reading_context=reading_context,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model_element is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout_element is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model_element is not None and layout_element is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            for sbgnml_subunit in momapy.sbgn.io.sbgnml._reading_parsing.get_subunits(
                sbgnml_entity_pool_or_subunit
            ):
                (
                    subunit_model_element,
                    subunit_layout_element,
                ) = cls._make_entity_pool_or_subunit(
                    reading_context=reading_context,
                    sbgnml_entity_pool_or_subunit=sbgnml_subunit,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model_element is not None:
                    model_element.subunits.add(subunit_model_element)
                    reading_context.xml_id_to_model_element[sbgnml_subunit.get("id")] = (
                        subunit_model_element
                    )
                    momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                        reading_context,
                        sbgnml_subunit,
                        subunit_model_element,
                    )
                if layout_element is not None:
                    layout_element.layout_elements.append(subunit_layout_element)
                    reading_context.xml_id_to_layout_element[sbgnml_subunit.get("id")] = (
                        subunit_layout_element
                    )
                if model_element is not None and layout_element is not None:
                    auxiliary_units_map_elements.append(
                        (
                            subunit_model_element,
                            subunit_layout_element,
                        )
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
            if model_element is not None and layout_element is not None:
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_activity(
        cls,
        reading_context,
        sbgnml_activity,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(
                sbgnml_activity, reading_context.map_key
            )
            model_element_cls, layout_element_cls = (
                momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            )
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_activity(
                reading_context, sbgnml_activity, model_element_cls
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_activity(
                reading_context, sbgnml_activity, layout_element_cls
            )
            auxiliary_units_map_elements = []
            for sbgnml_unit_of_information in (
                momapy.sbgn.io.sbgnml._reading_parsing.get_units_of_information(
                    sbgnml_activity
                )
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information(
                    reading_context=reading_context,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model_element is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout_element is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model_element is not None and layout_element is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.activities,
                    sbgnml_activity.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context, sbgnml_activity, model_element
                )
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    sbgnml_activity.get("id")
                ] = layout_element
            if model_element is not None and layout_element is not None:
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_state_variable(
        cls,
        reading_context,
        sbgnml_state_variable,
        super_model_element,
        super_layout_element,
        order=None,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_state_variable(
                reading_context, sbgnml_state_variable, order=order
            )
            sbgnml_state = getattr(sbgnml_state_variable, "state", None)
            if sbgnml_state is None:
                text = ""
            else:
                sbgnml_value = sbgnml_state.get("value")
                text = sbgnml_value if sbgnml_value is not None else ""
                sbgnml_variable = sbgnml_state.get("variable")
                if sbgnml_variable is not None:
                    text += f"@{sbgnml_variable}"
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_state_variable(
                reading_context, sbgnml_state_variable, text=text
            )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_unit_of_information(
        cls,
        reading_context,
        sbgnml_unit_of_information,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_subglyph_key(sbgnml_unit_of_information, reading_context.map_key)
            model_element_cls, layout_element_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_unit_of_information(
                reading_context, sbgnml_unit_of_information, model_element_cls
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_unit_of_information(
                reading_context, sbgnml_unit_of_information, layout_element_cls
            )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_submap(
        cls,
        reading_context,
        sbgnml_submap,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(
                sbgnml_submap, reading_context.map_key
            )
            model_element_cls, layout_element_cls = (
                momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            )
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_submap(
                reading_context, sbgnml_submap, model_element_cls
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_submap(
                reading_context, sbgnml_submap, layout_element_cls
            )
            terminal_map_elements = []
            reference_map_elements = []
            for sbgnml_terminal in (
                momapy.sbgn.io.sbgnml._reading_parsing.get_terminals(
                    sbgnml_submap
                )
            ):
                terminal_model = (
                    momapy.sbgn.io.sbgnml._reading_model.make_terminal_or_tag(
                        reading_context, sbgnml_terminal, is_terminal=True
                    )
                )
                terminal_layout = (
                    momapy.sbgn.io.sbgnml._reading_layout.make_terminal_or_tag(
                        reading_context, sbgnml_terminal, is_terminal=True
                    )
                )
                # Freeze terminal layout before creating references
                # (references need it as source)
                if terminal_layout is not None:
                    terminal_layout = momapy.builder.object_from_builder(
                        terminal_layout
                    )
                for sbgnml_equivalence_arc in (
                    momapy.sbgn.io.sbgnml._reading_parsing.get_equivalence_arcs(
                        sbgnml_terminal,
                        reading_context.xml_id_to_xml_element,
                        reading_context.sbgnml_glyph_id_to_sbgnml_arcs,
                    )
                ):
                    reference_model = (
                        momapy.sbgn.io.sbgnml._reading_model.make_reference(
                            reading_context, sbgnml_equivalence_arc, is_terminal=True
                        )
                    )
                    reference_layout = (
                        momapy.sbgn.io.sbgnml._reading_layout.make_reference(
                            reading_context, sbgnml_equivalence_arc, terminal_layout
                        )
                    )
                    if terminal_model is not None:
                        terminal_model.reference = reference_model
                    if reference_layout is not None:
                        reading_context.layout.layout_elements.append(reference_layout)
                    if reference_model is not None and reference_layout is not None:
                        reference_map_elements.append(
                            (
                                reference_model,
                                reference_layout,
                                sbgnml_terminal.get("id"),
                            )
                        )
                if terminal_model is not None:
                    terminal_model = momapy.builder.object_from_builder(
                        terminal_model
                    )
                    model_element.terminals.add(terminal_model)
                if terminal_layout is not None:
                    layout_element.layout_elements.append(terminal_layout)
                if terminal_model is not None and terminal_layout is not None:
                    terminal_map_elements.append(
                        (
                            terminal_model,
                            terminal_layout,
                            sbgnml_terminal.get("id"),
                        )
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.submaps,
                    sbgnml_submap.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context, sbgnml_submap, model_element
                )
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    sbgnml_submap.get("id")
                ] = layout_element
            if model_element is not None and layout_element is not None:
                # Build a lookup of terminal_xml_id -> terminal_model for
                # reference mapping
                terminal_model_by_xml_id = {
                    xml_id: t_model
                    for t_model, _, xml_id in terminal_map_elements
                }
                for (
                    terminal_model_el,
                    terminal_layout_el,
                    _,
                ) in terminal_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        terminal_layout_el,
                        (terminal_model_el, model_element),
                        replace=True,
                    )
                for (
                    ref_model,
                    ref_layout,
                    terminal_xml_id,
                ) in reference_map_elements:
                    terminal_model_el = terminal_model_by_xml_id.get(
                        terminal_xml_id
                    )
                    if terminal_model_el is not None:
                        reading_context.layout_model_mapping.add_mapping(
                            ref_layout,
                            (ref_model, terminal_model_el),
                            replace=True,
                        )
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_tag(
        cls,
        reading_context,
        sbgnml_tag,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            tag_model = momapy.sbgn.io.sbgnml._reading_model.make_terminal_or_tag(
                reading_context, sbgnml_tag, is_terminal=False
            )
            tag_layout = momapy.sbgn.io.sbgnml._reading_layout.make_terminal_or_tag(
                reading_context, sbgnml_tag, is_terminal=False
            )
            # Freeze tag layout before creating references
            # (references need it as source)
            if tag_layout is not None:
                tag_layout = momapy.builder.object_from_builder(tag_layout)
            reference_map_elements = []
            for sbgnml_equivalence_arc in (
                momapy.sbgn.io.sbgnml._reading_parsing.get_equivalence_arcs(
                    sbgnml_tag,
                    reading_context.xml_id_to_xml_element,
                    reading_context.sbgnml_glyph_id_to_sbgnml_arcs,
                )
            ):
                reference_model = (
                    momapy.sbgn.io.sbgnml._reading_model.make_reference(
                        reading_context, sbgnml_equivalence_arc, is_terminal=False
                    )
                )
                reference_layout = (
                    momapy.sbgn.io.sbgnml._reading_layout.make_reference(
                        reading_context, sbgnml_equivalence_arc, tag_layout
                    )
                )
                if tag_model is not None:
                    tag_model.reference = reference_model
                if reference_layout is not None:
                    reading_context.layout.layout_elements.append(reference_layout)
                if reference_model is not None and reference_layout is not None:
                    reference_map_elements.append(
                        (reference_model, reference_layout)
                    )
            if tag_model is not None:
                tag_model = momapy.builder.object_from_builder(tag_model)
                tag_model = momapy.io.utils.register_model_element(
                    reading_context,
                    tag_model,
                    reading_context.model.tags,
                    sbgnml_tag.get("id"),
                )
            if tag_layout is not None:
                reading_context.layout.layout_elements.append(tag_layout)
                reading_context.xml_id_to_layout_element[
                    sbgnml_tag.get("id")
                ] = tag_layout
            if tag_model is not None and tag_layout is not None:
                for (
                    reference_model_element,
                    reference_layout_element,
                ) in reference_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        reference_layout_element,
                        (reference_model_element, tag_model),
                        replace=True,
                    )
                reading_context.layout_model_mapping.add_mapping(
                    tag_layout, tag_model, replace=True
                )
        else:
            tag_model = None
            tag_layout = None
        return tag_model, tag_layout

    @classmethod
    def _make_and_add_phenotype(
        cls,
        reading_context,
        sbgnml_phenotype,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            model_element, layout_element = cls._make_entity_pool_or_subunit(
                reading_context=reading_context,
                sbgnml_entity_pool_or_subunit=sbgnml_phenotype,
                super_model_element=None,
                super_layout_element=None,
            )
            if model_element is not None:
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.processes,
                    sbgnml_phenotype.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context, sbgnml_phenotype, model_element
                )
            if layout_element is not None:
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    sbgnml_phenotype.get("id")
                ] = layout_element
            if model_element is not None and layout_element is not None:
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_stoichiometric_process(
        cls,
        reading_context,
        sbgnml_process,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(sbgnml_process, reading_context.map_key)
            model_element_cls, layout_element_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            model_element = (
                momapy.sbgn.io.sbgnml._reading_model.make_stoichiometric_process(
                    reading_context, sbgnml_process, model_element_cls
                )
            )
            layout_element = (
                momapy.sbgn.io.sbgnml._reading_layout.make_stoichiometric_process(
                    reading_context, sbgnml_process, layout_element_cls
                )
            )
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[sbgnml_process.get("id")] = (
                    layout_element
                )
            participant_map_elements = []
            sbgnml_consumption_arcs, sbgnml_production_arcs = (
                momapy.sbgn.io.sbgnml._reading_parsing.get_consumption_and_production_arcs(
                    sbgnml_process, reading_context.sbgnml_glyph_id_to_sbgnml_arcs
                )
            )
            for sbgnml_consumption_arc in sbgnml_consumption_arcs:
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant(
                        reading_context=reading_context,
                        sbgnml_consumption_arc=sbgnml_consumption_arc,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if model_element is not None and layout_element is not None:
                    participant_map_elements.append(
                        (reactant_model_element, reactant_layout_element)
                    )
            for sbgnml_production_arc in sbgnml_production_arcs:
                product_model_element, product_layout_element = (
                    cls._make_and_add_product(
                        reading_context=reading_context,
                        sbgnml_production_arc=sbgnml_production_arc,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_sbgnml_element=sbgnml_process,
                    )
                )
                if model_element is not None and layout_element is not None:
                    participant_map_elements.append(
                        (product_model_element, product_layout_element)
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.processes,
                    sbgnml_process.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context,
                    sbgnml_process,
                    model_element,
                )
            if model_element is not None and layout_element is not None:
                reading_context.layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element]
                        + [
                            participant_map_element[1]
                            for participant_map_element in participant_map_elements
                        ]
                        + [
                            participant_map_element[1].target
                            for participant_map_element in participant_map_elements
                        ]
                    ),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    participant_model_element,
                    participant_layout_element,
                ) in participant_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        participant_layout_element,
                        (participant_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant(
        cls,
        reading_context,
        sbgnml_consumption_arc,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_reactant(
                reading_context, sbgnml_consumption_arc
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_reactant(
                reading_context, sbgnml_consumption_arc, super_layout_element
            )
            if model_element is not None:
                super_model_element.reactants.add(model_element)
            if layout_element is not None:
                reading_context.layout.layout_elements.append(layout_element)
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product(
        cls,
        reading_context,
        sbgnml_production_arc,
        super_model_element,
        super_layout_element,
        super_sbgnml_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            process_direction = momapy.sbgn.io.sbgnml._reading_parsing.get_process_direction(
                super_sbgnml_element, reading_context.sbgnml_glyph_id_to_sbgnml_arcs
            )
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_product(
                reading_context,
                sbgnml_production_arc,
                super_model_element,
                super_sbgnml_element,
                process_direction,
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_product(
                reading_context, sbgnml_production_arc, super_layout_element
            )
            if model_element is not None:
                super_model_element.products.add(model_element)
            if layout_element is not None:
                reading_context.layout.layout_elements.append(layout_element)
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logical_operator(
        cls,
        reading_context,
        sbgnml_logical_operator,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_glyph_key(sbgnml_logical_operator, reading_context.map_key)
            model_element_cls, layout_element_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            model_element = momapy.sbgn.io.sbgnml._reading_model.make_logical_operator(
                reading_context, sbgnml_logical_operator, model_element_cls
            )
            layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_logical_operator(
                reading_context, sbgnml_logical_operator, layout_element_cls
            )
            if layout_element is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[sbgnml_logical_operator.get("id")] = (
                    layout_element
                )
            input_map_elements = []
            sbgnml_logic_arcs = momapy.sbgn.io.sbgnml._reading_parsing.get_logic_arcs(
                sbgnml_operator=sbgnml_logical_operator,
                sbgnml_id_to_sbgnml_element=reading_context.xml_id_to_xml_element,
                sbgnml_glyph_id_to_sbgnml_arcs=reading_context.sbgnml_glyph_id_to_sbgnml_arcs,
            )
            for sbgnml_logic_arc in sbgnml_logic_arcs:
                input_model_element, input_layout_element = (
                    cls._make_and_add_logical_operator_input(
                        reading_context=reading_context,
                        sbgnml_logic_arc=sbgnml_logic_arc,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if model_element is not None and layout_element is not None:
                    input_map_elements.append(
                        (input_model_element, input_layout_element)
                    )
            if model_element is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.logical_operators,
                    sbgnml_logical_operator.get("id"),
                )
            if model_element is not None and layout_element is not None:
                reading_context.layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element]
                        + [
                            input_map_element[1]
                            for input_map_element in input_map_elements
                        ]
                        + [
                            input_map_element[1].target
                            for input_map_element in input_map_elements
                        ]
                    ),  # TODO: add whole logical function tree?
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    input_model_element,
                    input_layout_element,
                ) in input_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        input_layout_element,
                        (input_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logical_operator_input(
        cls,
        reading_context,
        sbgnml_logic_arc,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            sbgnml_source_id = sbgnml_logic_arc.get("source")
            # We consider that the source can be the port of a logical operator.
            # Moreover this logical operator could have not yet been made
            sbgnml_source_element = reading_context.xml_id_to_xml_element[sbgnml_source_id]
            sbgnml_source_id = sbgnml_source_element.get("id")
            source_model_element = reading_context.xml_id_to_model_element.get(sbgnml_source_id)
            source_layout_element = reading_context.xml_id_to_layout_element.get(
                sbgnml_source_id
            )
            if source_model_element is None and source_layout_element is None:
                source_model_element, source_layout_element = (
                    cls._make_and_add_logical_operator(
                        reading_context=reading_context,
                        sbgnml_logical_operator=sbgnml_source_element,
                    )
                )
            model_element = (
                momapy.sbgn.io.sbgnml._reading_model.make_logical_operator_input(
                    reading_context, sbgnml_logic_arc, source_model_element
                )
            )
            layout_element = (
                momapy.sbgn.io.sbgnml._reading_layout.make_logical_operator_input(
                    reading_context, sbgnml_logic_arc, source_layout_element, super_layout_element
                )
            )
            if model_element is not None:
                super_model_element.inputs.add(model_element)
            if layout_element is not None:
                reading_context.layout.layout_elements.append(layout_element)
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation(
        cls,
        reading_context,
        sbgnml_modulation,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.sbgn.io.sbgnml._reading_classification.get_arc_key(sbgnml_modulation, reading_context.map_key)
            model_element_cls, layout_element_cls = momapy.sbgn.io.sbgnml._reading_classification.KEY_TO_CLASS[key]
            sbgnml_source_id = sbgnml_modulation.get("source")
            sbgnml_source_element = reading_context.xml_id_to_xml_element[sbgnml_source_id]
            sbgnml_source_id = sbgnml_source_element.get("id")
            sbgnml_target_id = sbgnml_modulation.get("target")
            if reading_context.model is not None:
                source_model_element = reading_context.xml_id_to_model_element[sbgnml_source_id]
                target_model_element = reading_context.xml_id_to_model_element[sbgnml_target_id]
                model_element = momapy.sbgn.io.sbgnml._reading_model.make_modulation(
                    reading_context, sbgnml_modulation, model_element_cls,
                    source_model_element, target_model_element
                )
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    (
                        reading_context.model.modulations
                        if momapy.sbgn.io.sbgnml._reading_classification.get_module(reading_context.map_key) == momapy.sbgn.pd
                        else reading_context.model.influences
                    ),
                    sbgnml_modulation.get("id"),
                )
                momapy.sbgn.io.sbgnml._reading_model.make_and_add_annotations_and_notes(
                    reading_context,
                    sbgnml_modulation,
                    model_element,
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                source_layout_element = reading_context.xml_id_to_layout_element[
                    sbgnml_source_id
                ]
                target_layout_element = reading_context.xml_id_to_layout_element[
                    sbgnml_target_id
                ]
                layout_element = momapy.sbgn.io.sbgnml._reading_layout.make_modulation(
                    reading_context, sbgnml_modulation, layout_element_cls,
                    source_layout_element, target_layout_element
                )
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[sbgnml_modulation.get("id")] = (
                    layout_element
                )
            else:
                layout_element = None
            if model_element is not None and layout_element is not None:
                source_mapping_key = reading_context.layout_model_mapping._singleton_to_key.get(
                    source_layout_element
                )
                if source_mapping_key is not None:
                    source_layout_elements = source_mapping_key
                else:
                    source_layout_elements = frozenset([source_layout_element])
                target_mapping_key = reading_context.layout_model_mapping._singleton_to_key.get(
                    target_layout_element
                )
                if target_mapping_key is not None:
                    target_layout_elements = target_mapping_key
                else:
                    target_layout_elements = frozenset([target_layout_element])
                reading_context.layout_model_mapping.add_mapping(
                    frozenset([layout_element])
                    | source_layout_elements
                    | target_layout_elements,
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_style_sheet(
        cls, layout, sbgnml_render_information, sbgnml_id_to_layout_element
    ):
        style_sheet = momapy.styling.StyleSheet()
        if sbgnml_render_information.background_color is not None:
            style_collection = momapy.styling.StyleCollection()
            layout_selector = momapy.styling.IdSelector(layout.id_)
            style_collection["fill"] = momapy.coloring.Color.from_hexa(
                sbgnml_render_information.background_color
            )
            style_sheet[layout_selector] = style_collection
        d_colors = {}
        if sbgnml_render_information.list_of_color_definitions is not None:
            for (
                color_definition
            ) in sbgnml_render_information.list_of_color_definitions.color_definition:
                color_hex = color_definition.value
                if len(color_hex) < 8:
                    color = momapy.coloring.Color.from_hex(color_hex)
                else:
                    color = momapy.coloring.Color.from_hexa(color_hex)
                d_colors[color_definition.id] = color
        if sbgnml_render_information.list_of_styles is not None:
            for style in sbgnml_render_information.list_of_styles.style:
                arc_ids = []
                node_ids = []
                for id_ in style.id_list.split(" "):
                    layout_element = sbgnml_id_to_layout_element.get(id_)
                    if layout_element is not None:
                        if momapy.builder.isinstance_or_builder(
                            layout_element, momapy.sbgn.core.SBGNNode
                        ):
                            node_ids.append(id_)
                        else:
                            arc_ids.append(id_)
                if node_ids:
                    node_style_collection = momapy.styling.StyleCollection()
                    for attr in ["fill", "stroke"]:
                        color_str = getattr(style.g, attr)
                        if color_str is not None:
                            color = d_colors.get(color_str)
                            if color is None:
                                color = momapy.coloring.Color.from_hex(color_str)
                            node_style_collection[attr] = color
                    for attr in ["stroke_width"]:
                        value = getattr(style.g, attr)
                        if value is not None:
                            node_style_collection[attr] = value
                    if node_style_collection:
                        node_selector = momapy.styling.OrSelector(
                            tuple(
                                [
                                    momapy.styling.IdSelector(node_id)
                                    for node_id in node_ids
                                ]
                            )
                        )
                        style_sheet[node_selector] = node_style_collection
                if arc_ids:
                    arc_style_collection = momapy.styling.StyleCollection()
                    for attr in ["fill", "stroke"]:
                        color_str = getattr(style.g, attr)
                        if color_str is not None:
                            color = d_colors.get(color_str)
                            if color is None:
                                color = momapy.coloring.Color.from_hex(color_str)
                            if attr == "stroke":
                                arc_style_collection[f"path_{attr}"] = color
                            arc_style_collection[f"arrowhead_{attr}"] = color
                    for attr in ["stroke_width"]:
                        value = getattr(style.g, attr)
                        if value is not None:
                            arc_style_collection[f"path_{attr}"] = value
                            arc_style_collection[f"arrowhead_{attr}"] = value
                    if arc_style_collection:
                        arc_selector = momapy.styling.OrSelector(
                            tuple([momapy.styling.IdSelector(id) for id in arc_ids])
                        )
                        style_sheet[arc_selector] = arc_style_collection
                label_style_collection = momapy.styling.StyleCollection()
                for attr in ["font_size", "font_family"]:
                    value = getattr(style.g, attr)
                    if value is not None:
                        label_style_collection[attr] = value
                for attr in ["font_color"]:
                    color_str = getattr(style.g, attr)
                    if color_str is not None:
                        color = d_colors.get(color_str)
                        if color is None:
                            if color_str == "#000":
                                color_str = "#000000"
                            color = momapy.coloring.Color.from_hex(color_str)
                        label_style_collection["fill"] = color
                if label_style_collection:
                    if node_ids:
                        node_label_selector = momapy.styling.ChildSelector(
                            node_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.layout.TextLayout.__name__
                            ),
                        )
                        style_sheet[node_label_selector] = label_style_collection
                    if arc_ids:
                        arc_label_selector = momapy.styling.ChildSelector(
                            arc_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.layout.TextLayout.__name__
                            ),
                        )
                        style_sheet[arc_label_selector] = label_style_collection
        return style_sheet


class SBGNML0_2Reader(_SBGNMLReader):
    """Class for SBGN-ML 0.2 reader objects"""

    @classmethod
    def _get_map_key(cls, sbgnml_map):
        key = momapy.sbgn.io.sbgnml._reading_parsing.transform_class(sbgnml_map.get("language"))
        return key

    @classmethod
    def check_file(cls, file_path):
        """Return `true` if the given file is an SBGN-ML 0.2 document, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://sbgn.org/libsbgn/0.2" in line:
                        return True
            return False
        except Exception:
            return False


class SBGNML0_3Reader(_SBGNMLReader):
    """Class for SBGN-ML 0.3 reader objects"""

    @classmethod
    def _get_map_key(cls, sbgnml_map):
        sbgnml_version = sbgnml_map.get("version")
        if sbgnml_version is not None:
            if "sbgn.pd" in sbgnml_version:
                return "PROCESS_DESCRIPTION"
            elif "sbgn.af" in sbgnml_version:
                return "ACTIVITY_FLOW"
            elif "sbgn.er" in sbgnml_version:
                return "ENTITY_RELATIONSHIP"
        else:
            return SBGNML0_2Reader._get_map_key(sbgnml_map)

    @classmethod
    def check_file(cls, file_path):
        """Return `true` if the given file is an SBGN-ML 0.3 document, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://sbgn.org/libsbgn/0.3" in line:
                        return True
            return False
        except Exception:
            return False
