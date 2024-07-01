import abc
import uuid
import collections

import frozendict
import xsdata.formats.dataclass.context
import xsdata.formats.dataclass.parsers
import xsdata.formats.dataclass.parsers.config
import xsdata.formats.dataclass.serializers
import xsdata.formats.dataclass.serializers.config

import momapy.__about__
import momapy.utils
import momapy.core
import momapy.io
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.styling
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.io._sbgnml_parser_0_2
import momapy.sbgn.io._sbgnml_parser_0_3


class _SBGNMLReader(momapy.io.MapReader):
    _DEFAULT_FONT_FAMILY = "Helvetica"
    _DEFAULT_FONT_SIZE = 14.0
    _DEFAULT_FONT_FILL = momapy.coloring.black
    _SBGNML_CLASS_TO_MAKE_AND_ADD_FUNC_NAME = {
        "STATE_VARIABLE": "_make_and_add_state_variable_from_sbgnml",
        "UNIT_OF_INFORMATION": "_make_and_add_unit_of_information_from_sbgnml",
        "TERMINAL": "_make_and_add_submap_terminal_from_sbgnml",
        "UNSPECIFIED_ENTITY_SUBUNIT": "_make_and_add_unspecified_entity_subunit_from_sbgnml",
        "MACROMOLECULE_SUBUNIT": "_make_and_add_macromolecule_subunit_from_sbgnml",
        "MACROMOLECULE_MULTIMER_SUBUNIT": "_make_and_add_macromolecule_multimer_subunit_from_sbgnml",
        "SIMPLE_CHEMICAL_SUBUNIT": "_make_and_add_simple_chemical_subunit_from_sbgnml",
        "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT": "_make_and_add_simple_chemical_multimer_subunit_from_sbgnml",
        "NUCLEIC_ACID_FEATURE_SUBUNIT": "_make_and_add_nucleic_acid_feature_subunit_from_sbgnml",
        "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT": "_make_and_add_nucleic_acid_feature_multimer_subunit_from_sbgnml",
        "COMPLEX_SUBUNIT": "_make_and_add_complex_subunit_from_sbgnml",
        "COMPLEX_MULTIMER_SUBUNIT": "_make_and_add_complex_multimer_subunit_from_sbgnml",
        "COMPARTMENT": "_make_and_add_compartment_from_sbgnml",
        "SUBMAP": "_make_and_add_submap_from_sbgnml",
        # "BIOLOGICAL_ACTIVITY": "_biological_activity_from_sbgnml",
        "UNSPECIFIED_ENTITY": "_make_and_add_unspecified_entity_from_sbgnml",
        "MACROMOLECULE": "_make_and_add_macromolecule_from_sbgnml",
        "MACROMOLECULE_MULTIMER": "_make_and_add_macromolecule_multimer_from_sbgnml",
        "SIMPLE_CHEMICAL": "_make_and_add_simple_chemical_from_sbgnml",
        "SIMPLE_CHEMICAL_MULTIMER": "_make_and_add_simple_chemical_multimer_from_sbgnml",
        "NUCLEIC_ACID_FEATURE": "_make_and_add_nucleic_acid_feature_from_sbgnml",
        "NUCLEIC_ACID_FEATURE_MULTIMER": "_make_and_add_nucleic_acid_feature_multimer_from_sbgnml",
        "COMPLEX": "_make_and_add_complex_from_sbgnml",
        "COMPLEX_MULTIMER": "_make_and_add_complex_multimer_from_sbgnml",
        "SOURCE_AND_SINK": "_make_and_add_empty_set_from_sbgnml",
        "PERTURBING_AGENT": "_make_and_add_perturbing_agent_from_sbgnml",
        "PROCESS": "_make_and_add_generic_process_from_sbgnml",
        "ASSOCIATION": "_make_and_add_association_from_sbgnml",
        "DISSOCIATION": "_make_and_add_dissociation_from_sbgnml",
        "UNCERTAIN_PROCESS": "_make_and_add_uncertain_process_from_sbgnml",
        "OMITTED_PROCESS": "_make_and_add_omitted_process_from_sbgnml",
        "PHENOTYPE": "_make_and_add_phenotype_from_sbgnml",
        # "UNIT_OF_INFORMATION_UNSPECIFIED_ENTITY": "_unit_of_information_unspecified_entity_elements_from_sbgnml",
        # "UNIT_OF_INFORMATION_MACROMOLECULE": "_unit_of_information_macromolecule_elements_from_sbgnml",
        # "UNIT_OF_INFORMATION_SIMPLE_CHEMICAL": "_unit_of_information_simple_chemical_elements_from_sbgnml",
        # "UNIT_OF_INFORMATION_NUCLEIC_ACID_FEATURE": "_unit_of_information_nucleic_acid_feature_elements_from_sbgnml",
        # "UNIT_OF_INFORMATION_COMPLEX": "_unit_of_information_complex_elements_from_sbgnml",
        # "UNIT_OF_INFORMATION_PERTURBATION": "_unit_of_information_perturbation_elements_from_sbgnml",
        "AND": "_make_and_add_and_operator_from_sbgnml",
        "OR": "_make_and_add_or_operator_from_sbgnml",
        "NOT": "_make_and_add_not_operator_from_sbgnml",
        # "DELAY": "_delay_operator_elements_from_sbgnml",
        "CONSUMPTION": "_make_and_add_consumption_from_sbgnml",
        "PRODUCTION": "_make_and_add_production_from_sbgnml",
        "MODULATION": "_make_and_add_modulation_from_sbgnml",
        "STIMULATION": "_make_and_add_stimulation_from_sbgnml",
        "CATALYSIS": "_make_and_add_catalysis_from_sbgnml",
        "NECESSARY_STIMULATION": "_make_and_add_necessary_stimulation_from_sbgnml",
        "INHIBITION": "_make_and_add_inhibition_from_sbgnml",
        # "POSITIVE_INFLUENCE": "_positive_influence_elements_from_arc",
        # "NEGATIVE_INFLUENCE": "_negative_influence_elements_from_arc",
        # "UNKNOWN_INFLUENCE": "_unknown_influence_elements_from_arc",
        "LOGIC_ARC_LOGICAL_OPERATOR": "_make_and_add_logical_operator_input_from_sbgnml",
        "LOGIC_ARC_EQUIVALENCE_OPERATOR": "_make_and_add_equivalence_operator_input_from_sbgnml",
        # "EQUIVALENCE_ARC": "_equivalence_arc_elements_from_arc",
        "TAG": "_make_and_add_tag_from_sbgnml",
    }
    _SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
        "encodes": momapy.sbgn.core.BQBiol.ENCODES,
        "has_part": momapy.sbgn.core.BQBiol.HAS_PART,
        "has_property": momapy.sbgn.core.BQBiol.HAS_PROPERTY,
        "has_version": momapy.sbgn.core.BQBiol.HAS_VERSION,
        "is_value": momapy.sbgn.core.BQBiol.IS,
        "is_described_by": momapy.sbgn.core.BQBiol.IS_DESCRIBED_BY,
        "is_encoded_by": momapy.sbgn.core.BQBiol.IS_ENCODED_BY,
        "is_homolog_to": momapy.sbgn.core.BQBiol.IS_HOMOLOG_TO,
        "is_part_of": momapy.sbgn.core.BQBiol.IS_PART_OF,
        "is_property_of": momapy.sbgn.core.BQBiol.IS_PROPERTY_OF,
        "is_version_of": momapy.sbgn.core.BQBiol.IS_VERSION_OF,
        "occurs_in": momapy.sbgn.core.BQBiol.OCCURS_IN,
        "has_taxon": momapy.sbgn.core.BQBiol.HAS_TAXON,
        "has_instance": momapy.sbgn.core.BQModel.HAS_INSTANCE,
        "biomodels_net_model_qualifiers_is": momapy.sbgn.core.BQModel.IS,
        "is_derived_from": momapy.sbgn.core.BQModel.IS_DERIVED_FROM,
        "biomodels_net_model_qualifiers_is_described_by": momapy.sbgn.core.BQModel.IS_DESCRIBED_BY,
        "is_instance_of": momapy.sbgn.core.BQModel.IS_INSTANCE_OF,
    }
    _parser_module = None

    @classmethod
    def read(
        cls,
        file_path,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        config = xsdata.formats.dataclass.parsers.config.ParserConfig()
        parser = xsdata.formats.dataclass.parsers.XmlParser(
            config=config,
            context=xsdata.formats.dataclass.context.XmlContext(),
        )
        sbgnml_sbgn = parser.parse(
            source=file_path, clazz=cls._parser_module.Sbgn
        )
        map_ = cls._make_map_from_sbgnml(
            sbgnml_sbgn=sbgnml_sbgn,
            with_render_information=with_render_information,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        return map_

    @classmethod
    def _make_map_from_sbgnml(
        cls,
        sbgnml_sbgn,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        sbgnml_id_to_model_element = {}
        sbgnml_id_to_layout_element = {}
        sbgnml_map = cls._get_sbgnml_map_from_sbgnml(sbgnml_sbgn)
        map_ = cls._make_map_no_subelements_from_sbgnml(sbgnml_map)
        # We gather glyph ids and their correponding glyphs
        sbgnml_id_to_sbgnml_element = {}
        for sbgnml_glyph in sbgnml_map.glyph:
            sub_sbgnml_id_to_sbgnml_element = (
                cls._get_sbgnml_id_to_sbgnml_element_from_sbgnml(sbgnml_glyph)
            )
            sbgnml_id_to_sbgnml_element |= sub_sbgnml_id_to_sbgnml_element
        for sbgnml_arc in sbgnml_map.arc:
            sub_sbgnml_id_to_sbgnml_element = (
                cls._get_sbgnml_id_to_sbgnml_element_from_sbgnml(sbgnml_arc)
            )
            sbgnml_id_to_sbgnml_element |= sub_sbgnml_id_to_sbgnml_element
        # We gather glyph ids and their ingoing/outgoing arcs
        sbgnml_glyph_id_to_sbgnml_arcs = collections.defaultdict(list)
        for sbgnml_arc in sbgnml_map.arc:
            sbgnml_source = sbgnml_id_to_sbgnml_element[sbgnml_arc.source]
            sbgnml_target = sbgnml_id_to_sbgnml_element[sbgnml_arc.target]
            sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_source.id].append(sbgnml_arc)
            sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_target.id].append(sbgnml_arc)
        sbgnml_id_super_sbgnml_id_for_mapping = (
            []
        )  # will serve for building the layout_model_mapping
        # We make model and layout elements from glyphs and arcs; when an arc or
        # a glyph references another sbgnml element, we make the model and
        # layout elements corresponding to that sbgnml element in most cases,
        # and add them to their super model or super layout element accordingly.
        # We make glyphs compartments first as they have to be in the background
        for sbgnml_glyph in sbgnml_map.glyph:
            if (
                sbgnml_glyph.class_value.name == "COMPARTMENT"
                and sbgnml_glyph.id not in sbgnml_id_to_model_element
            ):
                model_element, layout_element = (
                    cls._make_and_add_elements_from_sbgnml(
                        map_=map_,
                        sbgnml_element=sbgnml_glyph,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                        super_sbgnml_element=None,
                        super_model_element=None,
                        super_layout_element=None,
                        order=None,
                        with_annotations=with_annotations,
                    )
                )
        # We make the rest of the glyphs
        for sbgnml_glyph in sbgnml_map.glyph:
            if (
                sbgnml_glyph.class_value.name != "COMPARTMENT"
                and sbgnml_glyph.id not in sbgnml_id_to_model_element
            ):
                model_element, layout_element = (
                    cls._make_and_add_elements_from_sbgnml(
                        map_=map_,
                        sbgnml_element=sbgnml_glyph,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                        super_sbgnml_element=None,
                        super_model_element=None,
                        super_layout_element=None,
                        order=None,
                        with_annotations=with_annotations,
                    )
                )

        # We then make arcs
        for sbgnml_arc in sbgnml_map.arc:
            if sbgnml_arc.id not in sbgnml_id_to_model_element:
                model_element, layout_element = (
                    cls._make_and_add_elements_from_sbgnml(
                        map_=map_,
                        sbgnml_element=sbgnml_arc,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                        super_sbgnml_element=None,
                        super_model_element=None,
                        super_layout_element=None,
                        order=None,
                        with_annotations=with_annotations,
                    )
                )
        # We make the layout_model_mapping
        for (
            sbgnml_id,
            super_sbgnml_id,
        ) in sbgnml_id_super_sbgnml_id_for_mapping:
            model_element = sbgnml_id_to_model_element[sbgnml_id]
            if super_sbgnml_id is not None:
                super_model_element = sbgnml_id_to_model_element[
                    super_sbgnml_id
                ]
            else:
                super_model_element = None
            layout_element = sbgnml_id_to_layout_element[sbgnml_id]
            map_.add_mapping(
                (model_element, super_model_element), layout_element
            )
        # If the map has a bbox, we use it for the dimensions of the layout;
        # otherwise, we compute the dimensions from the layout elements
        if sbgnml_map.bbox is not None:
            position = cls._make_position_from_sbgnml(sbgnml_map)
            map_.layout.position = position
            map_.layout.width = sbgnml_map.bbox.w
            map_.layout.height = sbgnml_map.bbox.h
        else:
            momapy.positioning.set_fit(
                map_.layout,
                momapy.builder.object_from_builder(
                    map_.layout
                ).layout_elements,
            )
        if with_annotations:
            if (
                sbgnml_map.extension is not None
                and sbgnml_map.extension.annotation is not None
            ):
                annotations = cls._annotations_from_sbgnml(
                    map_, sbgnml_map.extension.annotation
                )
                for annotation in annotations:
                    map_.model.annotations.add(annotation)
        if with_notes and sbgnml_map.notes is not None:
            notes = cls._notes_from_sbgnml(sbgnml_map.notes)
            map_.notes = notes
        map_ = momapy.builder.object_from_builder(map_)
        if (
            with_render_information
            and sbgnml_map.extension is not None
            and sbgnml_map.extension.render_information is not None
        ):
            style_sheet = cls._style_sheet_from_sbgnml(
                map_,
                sbgnml_map.extension.render_information,
                sbgnml_id_to_layout_element,
            )
            map_ = momapy.styling.apply_style_sheet(map_, style_sheet)
        return map_

    @classmethod
    def _make_and_add_state_variable_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.StateVariable)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if sbgnml_element.state is None:
            value = None
            variable = None
            order = order
            text = ""
        else:
            if sbgnml_element.state.value is None:
                value = None
                text = ""
            else:
                value = sbgnml_element.state.value
                text = sbgnml_element.state.value
            if (
                sbgnml_element.state.variable is not None
                and sbgnml_element.state.variable
            ):
                variable = sbgnml_element.state.variable
                text += f"@{sbgnml_element.state.variable}"
                order = None
            else:
                variable = None
                order = order
        model_element.value = value
        model_element.variable = variable
        model_element.order = order
        if (
            sbgnml_element.extension is not None
            and sbgnml_element.extension.annotation is not None
        ):
            annotations = cls._annotations_from_sbgnml(
                map_, sbgnml_element.extension.annotation
            )
            for annotation in annotations:
                model_element.annotations.add(annotation)
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.StateVariableLayout
        )
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        text_layout = momapy.core.TextLayoutBuilder()
        text_layout.text = text
        text_layout.position = position
        text_layout.font_family = cls._DEFAULT_FONT_FAMILY
        text_layout.font_size = 8.0
        text_layout.fill = cls._DEFAULT_FONT_FILL
        text_layout = momapy.builder.object_from_builder(text_layout)
        layout_element.label = text_layout
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        super_model_element.state_variables.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_unit_of_information_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(
            momapy.sbgn.pd.UnitOfInformation
        )
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            l = sbgnml_element.label.text.split(":")
            model_element.value = l[-1]
            if len(l) > 1:
                model_element.prefix = l[0]
            text = sbgnml_element.label.text
        else:
            text = None
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.UnitOfInformationLayout
        )
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if text is not None:
            text_layout = momapy.core.TextLayoutBuilder()
            text_layout.text = text
            text_layout.position = position
            text_layout.font_family = cls._DEFAULT_FONT_FAMILY
            text_layout.font_size = 8.0
            text_layout.fill = cls._DEFAULT_FONT_FILL
            text_layout = momapy.builder.object_from_builder(text_layout)
            layout_element.label = text_layout
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        super_model_element.units_of_information.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_submap_terminal_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.SubmapTerminal)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.SubmapTerminalLayout
        )
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        layout_element.direction = cls._get_sbgnml_tag_direction(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the model and layout elements
        super_model_element.terminals.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_macromolecule_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.MacromoleculeSubunit,
            layout_element_cls=momapy.sbgn.pd.MacromoleculeSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_macromolecule_multimer_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.MacromoleculeMultimerSubunit,
            layout_element_cls=momapy.sbgn.pd.MacromoleculeMultimerSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_unspecified_entity_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.UnspecifiedEntitySubunit,
            layout_element_cls=momapy.sbgn.pd.UnspecifiedEntitySubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_simple_chemical_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.SimpleChemicalSubunit,
            layout_element_cls=momapy.sbgn.pd.SimpleChemicalSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_simple_chemical_multimer_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.SimpleChemicalMultimerSubunit,
            layout_element_cls=momapy.sbgn.pd.SimpleChemicalMultimerSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_nucleic_acid_feature_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NucleicAcidFeatureSubunit,
            layout_element_cls=momapy.sbgn.pd.NucleicAcidFeatureSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_nucleic_acid_feature_multimer_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunit,
            layout_element_cls=momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_complex_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.ComplexSubunit,
            layout_element_cls=momapy.sbgn.pd.ComplexSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_complex_multimer_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_subunit_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.ComplexMultimerSubunit,
            layout_element_cls=momapy.sbgn.pd.ComplexMultimerSubunitLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements
        super_model_element.subunits.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_compartment_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.Compartment)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.CompartmentLayout
        )
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We make and add the state variables, units of information, and
        # subunits to the model and layout elements.
        n_undefined_state_variables = 0
        for sbgnml_sub_element in sbgnml_element.glyph:
            sub_model_element, sub_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_sub_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=n_undefined_state_variables,
                )
            )
            if sbgnml_sub_element.class_value.name == "STATE_VARIABLE":
                if (
                    sbgnml_sub_element.state is None
                    or sbgnml_sub_element.state.variable is None
                    or not sbgnml_sub_element.state.variable
                ):
                    n_undefined_state_variables += 1
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        map_.layout.layout_elements.append(layout_element)
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.compartments,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_submap_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.Submap)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(momapy.sbgn.pd.SubmapLayout)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We make and add the state variables, units of information, and
        # subunits to the model and layout elements.
        n_undefined_state_variables = 0
        for sbgnml_sub_element in sbgnml_element.glyph:
            sub_model_element, sub_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_sub_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=n_undefined_state_variables,
                )
            )
            if sbgnml_sub_element.class_value.name == "STATE_VARIABLE":
                if (
                    sbgnml_sub_element.state is None
                    or sbgnml_sub_element.state.variable is None
                    or not sbgnml_sub_element.state.variable
                ):
                    n_undefined_state_variables += 1
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.submaps,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_unspecified_entity_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.UnspecifiedEntity,
            layout_element_cls=momapy.sbgn.pd.UnspecifiedEntityLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_macromolecule_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Macromolecule,
            layout_element_cls=momapy.sbgn.pd.MacromoleculeLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
            with_annotations=with_annotations,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_macromolecule_multimer_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.MacromoleculeMultimer,
            layout_element_cls=momapy.sbgn.pd.MacromoleculeMultimerLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_simple_chemical_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.SimpleChemical,
            layout_element_cls=momapy.sbgn.pd.SimpleChemicalLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_simple_chemical_multimer_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.SimpleChemicalMultimer,
            layout_element_cls=momapy.sbgn.pd.SimpleChemicalMultimerLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_nucleic_acid_feature_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NucleicAcidFeature,
            layout_element_cls=momapy.sbgn.pd.NucleicAcidFeatureLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_nucleic_acid_feature_multimer_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NucleicAcidFeatureMultimer,
            layout_element_cls=momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_complex_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Complex,
            layout_element_cls=momapy.sbgn.pd.ComplexLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_complex_multimer_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.ComplexMultimer,
            layout_element_cls=momapy.sbgn.pd.ComplexMultimerLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_perturbing_agent_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.PerturbingAgent,
            layout_element_cls=momapy.sbgn.pd.PerturbingAgentLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_empty_set_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_entity_pool_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.EmptySet,
            layout_element_cls=momapy.sbgn.pd.EmptySetLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.entity_pools,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_generic_process_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_process_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.GenericProcess,
            layout_element_cls=momapy.sbgn.pd.GenericProcessLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_omitted_process_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_process_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.OmittedProcess,
            layout_element_cls=momapy.sbgn.pd.OmittedProcessLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_uncertain_process_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_process_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.UncertainProcess,
            layout_element_cls=momapy.sbgn.pd.UncertainProcessLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_association_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_process_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Association,
            layout_element_cls=momapy.sbgn.pd.AssociationLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_dissociation_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_process_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Dissociation,
            layout_element_cls=momapy.sbgn.pd.DissociationLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the model and layout elements to the map_, and to the mapping
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_phenotype_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.Phenotype)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.PhenotypeLayout
        )
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We make and add the state variables, units of information, and
        # subunits to the model and layout elements.
        n_undefined_state_variables = 0
        for sbgnml_sub_element in sbgnml_element.glyph:
            sub_model_element, sub_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_sub_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=n_undefined_state_variables,
                )
            )
            if sbgnml_sub_element.class_value.name == "STATE_VARIABLE":
                if (
                    sbgnml_sub_element.state is None
                    or sbgnml_sub_element.state.variable is None
                    or not sbgnml_sub_element.state.variable
                ):
                    n_undefined_state_variables += 1
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = momapy.utils.get_or_return_element_from_collection(
            model_element, map_.model.processes
        )
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.processes,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_consumption_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.Reactant)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        sbgnml_source_id = sbgnml_element.source
        sbgnml_source_element = sbgnml_id_to_sbgnml_element[sbgnml_source_id]
        role_model_element = sbgnml_id_to_model_element.get(
            sbgnml_source_element.id
        )
        role_layout_element = sbgnml_id_to_layout_element.get(
            sbgnml_source_element.id
        )
        # In the case the source has not yet been made
        if role_model_element is None:
            role_model_element, role_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_source_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=super_sbgnml_element,
                )
            )
        model_element.element = role_model_element
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.ConsumptionLayout
        )
        sbgnml_points = (
            [sbgnml_element.end]
            + sbgnml_element.next[::-1]
            + [sbgnml_element.start]
        )
        # The source becomes the target: in momapy flux arcs go from the process
        # to the entity pool node; this way reversible consumptions can be
        # represented with production layouts. Also, no source
        # (the process layout) is set for the flux arc, so that we do not have a
        # circular definition that would be problematic when building the
        # object.
        for i, sbgnml_current_point in enumerate(sbgnml_points[1:]):
            sbgnml_previous_point = sbgnml_points[i]
            current_point = momapy.geometry.Point(
                sbgnml_current_point.x, sbgnml_current_point.y
            )
            previous_point = momapy.geometry.Point(
                sbgnml_previous_point.x, sbgnml_previous_point.y
            )
            segment = momapy.geometry.Segment(previous_point, current_point)
            layout_element.segments.append(segment)
        layout_element.target = role_layout_element
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        super_model_element.reactants.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_production_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element.
        # The model element class depends on whether the process is reversible
        # or not, the directionality of the process, and the position of the
        # arc relative to the position of the process.
        sbgnml_process_id = sbgnml_element.source
        sbgnml_process = sbgnml_id_to_sbgnml_element[sbgnml_process_id]
        if cls._is_sbgnml_process_reversible(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        ):
            process_direction = cls._get_sbgnml_process_direction(
                sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
            )
            if process_direction == momapy.core.Direction.HORIZONTAL:
                if sbgnml_element.start.x > sbgnml_process.bbox.x:  # RIGHT
                    model_element_cls = momapy.sbgn.pd.Product
                else:
                    model_element_cls = momapy.sbgn.pd.Reactant  # LEFT
            else:
                if sbgnml_element.start.y > sbgnml_process.bbox.y:  # TOP
                    model_element_cls = momapy.sbgn.pd.Product
                else:
                    model_element_cls = momapy.sbgn.pd.Reactant  # BOTTOM
        else:
            model_element_cls = momapy.sbgn.pd.Product
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        sbgnml_target_id = sbgnml_element.target
        sbgnml_target_element = sbgnml_id_to_sbgnml_element[sbgnml_target_id]
        role_model_element = sbgnml_id_to_model_element.get(
            sbgnml_target_element.id
        )
        role_layout_element = sbgnml_id_to_layout_element.get(
            sbgnml_target_element.id
        )
        # In the case the target has not yet been made
        if role_model_element is None:
            role_model_element, role_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_target_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    super_sbgnml_element=super_sbgnml_element,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                )
            )
        model_element.element = role_model_element
        # We make the layout element
        layout_element = map_.new_layout_element(
            momapy.sbgn.pd.ProductionLayout
        )
        sbgnml_points = (
            [sbgnml_element.start] + sbgnml_element.next + [sbgnml_element.end]
        )
        for i, sbgnml_current_point in enumerate(sbgnml_points[1:]):
            sbgnml_previous_point = sbgnml_points[i]
            current_point = momapy.geometry.Point(
                sbgnml_current_point.x, sbgnml_current_point.y
            )
            previous_point = momapy.geometry.Point(
                sbgnml_previous_point.x, sbgnml_previous_point.y
            )
            segment = momapy.geometry.Segment(previous_point, current_point)
            layout_element.segments.append(segment)
        layout_element.target = role_layout_element
        # We build the elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        super_model_element.products.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_logical_operator_input_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(
            momapy.sbgn.pd.LogicalOperatorInput
        )
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        sbgnml_source_id = sbgnml_element.source
        sbgnml_source_element = sbgnml_id_to_sbgnml_element[sbgnml_source_id]
        role_model_element = sbgnml_id_to_model_element.get(
            sbgnml_source_element.id
        )
        role_layout_element = sbgnml_id_to_layout_element.get(
            sbgnml_source_element.id
        )
        # In the case the source has not yet been made
        if role_model_element is None:
            role_model_element, role_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_source_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=super_sbgnml_element,
                )
            )
        model_element.element = role_model_element
        # We make the layout element
        layout_element = map_.new_layout_element(momapy.sbgn.pd.LogicArcLayout)
        sbgnml_points = (
            [sbgnml_element.end]
            + sbgnml_element.next[::-1]
            + [sbgnml_element.start]
        )
        # The source becomes the target: in momapy logic arcs go from the
        # operator to the input node.
        for i, sbgnml_current_point in enumerate(sbgnml_points[1:]):
            sbgnml_previous_point = sbgnml_points[i]
            current_point = momapy.geometry.Point(
                sbgnml_current_point.x, sbgnml_current_point.y
            )
            previous_point = momapy.geometry.Point(
                sbgnml_previous_point.x, sbgnml_previous_point.y
            )
            segment = momapy.geometry.Segment(previous_point, current_point)
            layout_element.segments.append(segment)
        layout_element.target = role_layout_element
        # We build the model and layout elements.
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        super_model_element.inputs.add(model_element)
        super_layout_element.layout_elements.append(layout_element)
        # We save de model and layout elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append(
            (sbgnml_element.id, super_sbgnml_element.id)
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_modulation_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Modulation,
            layout_element_cls=momapy.sbgn.pd.ModulationLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.modulations,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_stimulation_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_modulation_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Stimulation,
            layout_element_cls=momapy.sbgn.pd.StimulationLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.modulations,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibition_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_modulation_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Inhibition,
            layout_element_cls=momapy.sbgn.pd.InhibitionLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.modulations,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalysis_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_modulation_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.Catalysis,
            layout_element_cls=momapy.sbgn.pd.CatalysisLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.modulations,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_necessary_stimulation_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_modulation_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NecessaryStimulation,
            layout_element_cls=momapy.sbgn.pd.NecessaryStimulationLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.modulations,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_and_operator_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_operator_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.AndOperator,
            layout_element_cls=momapy.sbgn.pd.AndOperatorLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.logical_operators,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_or_operator_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_operator_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.OrOperator,
            layout_element_cls=momapy.sbgn.pd.OrOperatorLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.logical_operators,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_not_operator_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        model_element, layout_element = cls._make_operator_from_sbgnml(
            map_=map_,
            sbgnml_element=sbgnml_element,
            model_element_cls=momapy.sbgn.pd.NotOperator,
            layout_element_cls=momapy.sbgn.pd.NotOperatorLayout,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
            super_sbgnml_element=super_sbgnml_element,
        )
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.logical_operators,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_and_add_tag_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(momapy.sbgn.pd.Tag)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(momapy.sbgn.pd.TagLayout)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        layout_element.direction = cls._get_sbgnml_tag_direction(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        model_element = momapy.utils.get_or_return_element_from_collection(
            model_element, map_.model.tags
        )
        layout_element = momapy.builder.object_from_builder(layout_element)
        # We add the elements
        model_element = momapy.utils.add_ore_replace_element_in_set(
            model_element,
            map_.model.tags,
            func=lambda element, existing_element: element.id
            < existing_element.id,
        )
        map_.layout.layout_elements.append(layout_element)
        # We save the elements
        sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        # We save the ids for the mapping
        sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        return model_element, layout_element

    @classmethod
    def _make_entity_pool_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        model_element_cls,
        layout_element_cls,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        with_annotations=True,
    ):
        # We make the model element
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if sbgnml_element.compartment_ref is not None:
            compartment_model_element = sbgnml_id_to_model_element.get(
                sbgnml_element.compartment_ref
            )
            if compartment_model_element is None:
                sbgnml_compartment = sbgnml_id_to_sbgnml_element[
                    sbgnml_element.compartment_ref
                ]
                compartment_mode_element, _ = (
                    cls._make_and_add_elements_from_sbgnml(
                        map_=map_,
                        sbgnml_element=sbgnml_compartment,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    )
                )
            model_element.compartment = compartment_model_element
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        if (
            sbgnml_element.extension is not None
            and sbgnml_element.extension.annotation is not None
        ):
            annotations = cls._annotations_from_sbgnml(
                map_, sbgnml_element.extension.annotation
            )
            for annotation in annotations:
                model_element.annotations.add(annotation)
        # We make the layout element
        layout_element = map_.new_layout_element(layout_element_cls)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We make and add the state variables, units of information, and
        # subunits to the model and layout elements.
        n_undefined_state_variables = 0
        for sbgnml_sub_element in sbgnml_element.glyph:
            sub_model_element, sub_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_sub_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=n_undefined_state_variables,
                )
            )
            if sbgnml_sub_element.class_value.name == "STATE_VARIABLE":
                if (
                    sbgnml_sub_element.state is None
                    or sbgnml_sub_element.state.variable is None
                    or not sbgnml_sub_element.state.variable
                ):
                    n_undefined_state_variables += 1
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_subunit_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        model_element_cls,
        layout_element_cls,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
    ):
        # We make the model element
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            model_element.label = sbgnml_element.label.text
        # We make the layout element
        layout_element = map_.new_layout_element(layout_element_cls)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        if (
            sbgnml_element.label is not None
            and sbgnml_element.label.text is not None
        ):
            text_layout = cls._make_text_layout_from_sbgnml(
                sbgnml_label=sbgnml_element.label, position=position
            )
            layout_element.label = text_layout
        # We make and add the state variables, units of information, and
        # subunits to the model and layout elements.
        n_undefined_state_variables = 0
        for sbgnml_sub_element in sbgnml_element.glyph:
            sub_model_element, sub_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_sub_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=n_undefined_state_variables,
                )
            )
            if sbgnml_sub_element.class_value.name == "STATE_VARIABLE":
                if (
                    sbgnml_sub_element.state is None
                    or sbgnml_sub_element.state.variable is None
                    or not sbgnml_sub_element.state.variable
                ):
                    n_undefined_state_variables += 1
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_process_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        model_element_cls,
        layout_element_cls,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
    ):
        # We make the model element
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        model_element.reversible = cls._is_sbgnml_process_reversible(
            sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
        )
        sbgnml_consumption_arcs, sbgnml_production_arcs = (
            cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
            )
        )
        # We make the layout element
        layout_element = map_.new_layout_element(layout_element_cls)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        layout_element.direction = cls._get_sbgnml_process_direction(
            sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
        )
        layout_element.left_to_right = cls._is_sbgnml_process_left_to_right(
            sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
        )
        # We set the length of the connectors using the ports
        left_connector_length, right_connector_length = (
            cls._get_connectors_length_from_sbgnml(sbgnml_element)
        )
        if left_connector_length is not None:
            layout_element.left_connector_length = left_connector_length
        if right_connector_length is not None:
            layout_element.right_connector_length = right_connector_length
        # We add the reactants and products to the model element, and the
        # corresponding layouts to the layout element. If needed we make them.
        for sbgnml_consumption_arc in sbgnml_consumption_arcs:
            reactant_model_element = sbgnml_id_to_model_element.get(
                sbgnml_consumption_arc.id
            )
            reactant_layout_element = sbgnml_id_to_layout_element.get(
                sbgnml_consumption_arc.id
            )
            if reactant_model_element is None:
                (
                    reactant_model_element,
                    reactant_layout_element,
                ) = cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_consumption_arc,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=None,
                    with_annotations=True,
                )
        for sbgnml_production_arc in sbgnml_production_arcs:
            product_model_element = sbgnml_id_to_model_element.get(
                sbgnml_production_arc.id
            )
            product_layout_element = sbgnml_id_to_layout_element.get(
                sbgnml_production_arc.id
            )
            if product_model_element is None:
                (
                    product_model_element,
                    product_layout_element,
                ) = cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_production_arc,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    order=None,
                    with_annotations=True,
                )
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_operator_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        model_element_cls,
        layout_element_cls,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
    ):
        # We make the model element
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        # We make the layout element
        layout_element = map_.new_layout_element(layout_element_cls)
        layout_element.id = sbgnml_element.id
        position = cls._make_position_from_sbgnml(
            sbgnml_element=sbgnml_element
        )
        layout_element.position = position
        layout_element.width = sbgnml_element.bbox.w
        layout_element.height = sbgnml_element.bbox.h
        layout_element.direction = cls._get_sbgnml_process_direction(
            sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
        )
        layout_element.left_to_right = cls._is_sbgnml_operator_left_to_right(
            sbgnml_operator=sbgnml_element,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
        )
        # We set the length of the connectors using the ports
        left_connector_length, right_connector_length = (
            cls._get_connectors_length_from_sbgnml(sbgnml_element)
        )
        if left_connector_length is not None:
            layout_element.left_connector_length = left_connector_length
        if right_connector_length is not None:
            layout_element.right_connector_length = right_connector_length
        # We add inputs to the model and layout elements. We make them if needed
        sbgnml_logic_arcs = cls._get_sbgnml_logic_arcs_from_sbgnml_operator(
            sbgnml_operator=sbgnml_element,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
        )
        for sbgnml_logic_arc in sbgnml_logic_arcs:
            input_model_element = sbgnml_id_to_model_element.get(
                sbgnml_logic_arc.id
            )
            input_layout_element = sbgnml_id_to_layout_element.get(
                sbgnml_logic_arc.id
            )
            if input_model_element is None:
                (
                    input_model_element,
                    input_layout_element,
                ) = cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_logic_arc,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=sbgnml_element,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_modulation_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        model_element_cls,
        layout_element_cls,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cls._make_model_element_id_from_sbgnml(
            sbgnml_element
        )
        # We get the source model and layout elements. We make them if needed
        sbgnml_source_id = sbgnml_element.source
        sbgnml_source_element = sbgnml_id_to_sbgnml_element[sbgnml_source_id]
        source_model_element = sbgnml_id_to_model_element.get(
            sbgnml_source_element.id
        )
        source_layout_element = sbgnml_id_to_layout_element.get(
            sbgnml_source_element.id
        )
        if source_model_element is None:
            source_model_element, source_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_source_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                    super_sbgnml_element=super_sbgnml_element,
                )
            )
        model_element.source = source_model_element
        # We get the target model and layout elements. We make them if needed
        sbgnml_target_id = sbgnml_element.target
        sbgnml_target_element = sbgnml_id_to_sbgnml_element[sbgnml_target_id]
        target_model_element = sbgnml_id_to_model_element.get(
            sbgnml_target_element.id
        )
        target_layout_element = sbgnml_id_to_layout_element.get(
            sbgnml_target_element.id
        )
        if target_model_element is None:
            target_model_element, target_layout_element = (
                cls._make_and_add_elements_from_sbgnml(
                    map_=map_,
                    sbgnml_element=sbgnml_target_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    super_sbgnml_element=super_sbgnml_element,
                )
            )
        model_element.target = target_model_element
        # We make the layout element
        layout_element = map_.new_layout_element(layout_element_cls)
        sbgnml_points = (
            [sbgnml_element.start] + sbgnml_element.next + [sbgnml_element.end]
        )
        for i, sbgnml_current_point in enumerate(sbgnml_points[1:]):
            sbgnml_previous_point = sbgnml_points[i]
            current_point = momapy.geometry.Point(
                sbgnml_current_point.x, sbgnml_current_point.y
            )
            previous_point = momapy.geometry.Point(
                sbgnml_previous_point.x, sbgnml_previous_point.y
            )
            segment = momapy.geometry.Segment(previous_point, current_point)
            layout_element.segments.append(segment)
        layout_element.source = source_layout_element
        layout_element.target = target_layout_element
        # We build the model and layout elements
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_model_element_id_from_sbgnml(cls, sbgnml_element):
        return f"{sbgnml_element.id}"

    @classmethod
    @abc.abstractmethod
    def _get_sbgnml_map_from_sbgnml(cls, sbgnml_sbgn):
        return NotImplemented

    @classmethod
    @abc.abstractmethod
    def _make_map_no_subelements_from_sbgnml(cls, sbgnml_map):
        return NotImplemented

    @classmethod
    def _get_sbgnml_id_to_sbgnml_element_from_sbgnml(cls, sbgnml_element):
        sbgnml_id_to_sbgnml_element = {}
        sbgnml_id_to_sbgnml_element[sbgnml_element.id] = sbgnml_element
        if sbgnml_element.port:
            for sbgnml_port in sbgnml_element.port:
                sbgnml_id_to_sbgnml_element[sbgnml_port.id] = sbgnml_element
        if sbgnml_element.glyph:
            for sbgnml_glyph in sbgnml_element.glyph:
                sub_sbgnml_id_to_sbgnml_element = (
                    cls._get_sbgnml_id_to_sbgnml_element_from_sbgnml(
                        sbgnml_glyph
                    )
                )
                sbgnml_id_to_sbgnml_element |= sub_sbgnml_id_to_sbgnml_element
        return sbgnml_id_to_sbgnml_element

    @classmethod
    def _make_and_add_elements_from_sbgnml(
        cls,
        map_,
        sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
    ):
        make_and_add_func = cls._get_make_and_add_func_from_sbgnml(
            sbgnml_element=sbgnml_element,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            super_sbgnml_element=super_sbgnml_element,
        )
        if make_and_add_func is not None:
            model_element, layout_element = make_and_add_func(
                map_=map_,
                sbgnml_element=sbgnml_element,
                sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                super_sbgnml_element=super_sbgnml_element,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                order=order,
            )
        else:
            model_element = None
            layout_element = None
            print(f"no reading function for {sbgnml_element.class_value.name}")
        return model_element, layout_element

    @classmethod
    def _get_make_and_add_func_from_sbgnml(
        cls,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        super_sbgnml_element=None,
    ):
        sbgnml_element_class_str = sbgnml_element.class_value.name
        if super_sbgnml_element is not None:
            super_sbgnml_element_class_str = (
                super_sbgnml_element.class_value.name
            )
        else:
            super_sbgnml_element_class_str = None
        # Need to distinguish between biological activities' units of info
        if (
            super_sbgnml_element_class_str == "BIOLOGICAL_ACTIVITY"
            and sbgnml_element_class_str == "UNIT_OF_INFORMATION"
        ):
            key = (
                f"{sbgnml_element_class_str}_{sbgnml_element.entity.name.name}"
            )
        # Need to distinguish between complexes' subunits
        elif (
            super_sbgnml_element_class_str == "COMPLEX"
            and sbgnml_element_class_str
            in [
                "UNSPECIFIED_ENTITY",
                "MACROMOLECULE",
                "MACROMOLECULE_MULTIMER",
                "SIMPLE_CHEMICAL",
                "SIMPLE_CHEMICAL_MULTIMER",
                "NUCLEIC_ACID_FEATURE",
                "NUCLEIC_ACID_FEATURE_MULTIMER",
                "COMPLEX",
                "COMPLEX_MULTIMER",
            ]
        ):
            key = f"{sbgnml_element_class_str}_SUBUNIT"
        # A tag inside a submap is a terminal
        elif (
            super_sbgnml_element_class_str == "SUBMAP"
            and sbgnml_element_class_str == "TAG"
        ):
            key = "TERMINAL"
        # Need to distinguish between a logical operator input and a
        # equivalence operator input
        elif sbgnml_element_class_str == "LOGIC_ARC":
            sbgnml_target_id = sbgnml_element.target
            sbgnml_target = sbgnml_id_to_sbgnml_element[sbgnml_target_id]
            if sbgnml_target.class_value.name in [
                "AND",
                "OR",
                "NOT",
                "DELAY",
            ]:
                key = "LOGIC_ARC_LOGICAL_OPERATOR"
            else:
                key = "LOGIC_ARC_EQUIVALENCE_OPERATOR"
        else:
            key = sbgnml_element_class_str
        make_and_add_func_name = (
            cls._SBGNML_CLASS_TO_MAKE_AND_ADD_FUNC_NAME.get(key)
        )
        if make_and_add_func_name is None:
            return None
        return getattr(cls, make_and_add_func_name)

    @classmethod
    def _get_connectors_length_from_sbgnml(cls, sbgnml_element):
        left_connector_length = None
        right_connector_length = None
        for sbgnml_port in sbgnml_element.port:
            if sbgnml_port.x < sbgnml_element.bbox.x:  # LEFT
                left_connector_length = sbgnml_element.bbox.x - sbgnml_port.x
            elif sbgnml_port.y < sbgnml_element.bbox.y:  # UP
                left_connector_length = sbgnml_element.bbox.y - sbgnml_port.y
            elif (
                sbgnml_port.x >= sbgnml_element.bbox.x + sbgnml_element.bbox.w
            ):  # RIGHT
                right_connector_length = (
                    sbgnml_port.x
                    - sbgnml_element.bbox.x
                    - sbgnml_element.bbox.w
                )
            elif (
                sbgnml_port.y >= sbgnml_element.bbox.y + sbgnml_element.bbox.h
            ):  # DOWN
                right_connector_length = (
                    sbgnml_port.y
                    - sbgnml_element.bbox.y
                    - sbgnml_element.bbox.h
                )
        return left_connector_length, right_connector_length

    @classmethod
    def _get_sbgnml_logic_arcs_from_sbgnml_operator(
        cls,
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    ):
        sbgnml_logic_arcs = []
        for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_operator.id]:
            if (
                sbgnml_arc.class_value.name == "LOGIC_ARC"
                and sbgnml_id_to_sbgnml_element[sbgnml_arc.target]
                == sbgnml_operator
            ):
                sbgnml_logic_arcs.append(sbgnml_arc)
        return sbgnml_logic_arcs

    @classmethod
    def _make_position_from_sbgnml(cls, sbgnml_element):
        position = momapy.geometry.Point(
            sbgnml_element.bbox.x + sbgnml_element.bbox.w / 2,
            sbgnml_element.bbox.y + sbgnml_element.bbox.h / 2,
        )
        return position

    @classmethod
    def _make_text_layout_from_sbgnml(cls, sbgnml_label, position=None):
        text_layout = momapy.core.TextLayoutBuilder()
        if sbgnml_label.bbox is not None:
            position = cls._make_position_from_sbgnml(sbgnml_label)
        text_layout.position = position
        text_layout.text = sbgnml_label.text
        text_layout.font_family = cls._DEFAULT_FONT_FAMILY
        text_layout.font_size = cls._DEFAULT_FONT_SIZE
        text_layout.fill = cls._DEFAULT_FONT_FILL
        text_layout = momapy.builder.object_from_builder(text_layout)
        return text_layout

    @classmethod
    def _get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        sbgnml_consumption_arcs = []
        sbgnml_production_arcs = []
        for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_process.id]:
            if sbgnml_arc.class_value.name == "CONSUMPTION":
                sbgnml_consumption_arcs.append(sbgnml_arc)
            elif sbgnml_arc.class_value.name == "PRODUCTION":
                sbgnml_production_arcs.append(sbgnml_arc)
        return sbgnml_consumption_arcs, sbgnml_production_arcs

    @classmethod
    def _get_sbgnml_process_direction(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        for sbgnml_port in sbgnml_process.port:
            if (
                sbgnml_port.x < sbgnml_process.bbox.x
                or sbgnml_port.x
                >= sbgnml_process.bbox.x + sbgnml_process.bbox.w
            ):  # LEFT OR RIGHT
                direction = momapy.core.Direction.HORIZONTAL
            else:
                direction = momapy.core.Direction.VERTICAL
            break
        return direction

    @classmethod
    def _get_sbgnml_tag_direction(cls, sbgnml_tag):
        direction = momapy.core.Direction.RIGHT
        if sbgnml_tag.orientation.name == "UP":
            direction = momapy.core.Direction.UP
        elif sbgnml_tag.orientation.name == "RIGHT":
            direction = momapy.core.Direction.RIGHT
        elif sbgnml_tag.orientation.name == "DOWN":
            direction = momapy.core.Direction.DOWN
        elif sbgnml_tag.orientation.name == "LEFT":
            direction = momapy.core.Direction.LEFT
        return direction

    @classmethod
    def _is_sbgnml_operator_left_to_right(
        cls,
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    ):
        sbgnml_logic_arcs = cls._get_sbgnml_logic_arcs_from_sbgnml_operator(
            sbgnml_operator,
            sbgnml_id_to_sbgnml_element,
            sbgnml_glyph_id_to_sbgnml_arcs,
        )
        operator_direction = cls._get_sbgnml_process_direction(
            sbgnml_operator, sbgnml_glyph_id_to_sbgnml_arcs
        )
        for sbgnml_logic_arc in sbgnml_logic_arcs:
            if operator_direction == momapy.core.Direction.HORIZONTAL:
                if sbgnml_logic_arc.end.x < sbgnml_operator.bbox.x:
                    return True
                else:
                    return False
            else:
                if sbgnml_logic_arc.end.y < sbgnml_operator.bbox.y:
                    return True
                else:
                    return False
        return True

    @classmethod
    def _is_sbgnml_process_left_to_right(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        process_direction = cls._get_sbgnml_process_direction(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
        sbgnml_consumption_arcs, sbgnml_production_arcs = (
            cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
            )
        )
        if sbgnml_consumption_arcs:  # process is not reversible
            sbgnml_consumption_arc = sbgnml_consumption_arcs[0]
            sbgnml_production_arc = sbgnml_production_arcs[0]
            if process_direction == momapy.core.Direction.HORIZONTAL:
                if sbgnml_consumption_arc.end.x < sbgnml_production_arc.end.x:
                    return True
                else:
                    return False
            else:
                if sbgnml_consumption_arc.end.y < sbgnml_production_arc.end.y:
                    return True
                else:
                    return False
        # If the process is reversible, it defaults to left to right
        return True

    @classmethod
    def _is_sbgnml_process_reversible(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        sbgnml_consumption_arcs, sbgnml_consumption_arcs = (
            cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
            )
        )
        if sbgnml_consumption_arcs:
            return False
        return True

    @classmethod
    def _style_sheet_from_sbgnml(
        cls, map_, sbgnml_render_information, sbgnml_id_to_layout_element
    ):
        style_sheet = momapy.styling.StyleSheet()
        if sbgnml_render_information.background_color is not None:
            style_collection = momapy.styling.StyleCollection()
            layout_selector = momapy.styling.IdSelector(map_.layout.id)
            style_collection["fill"] = momapy.coloring.Color.from_hexa(
                sbgnml_render_information.background_color
            )
            style_sheet[layout_selector] = style_collection
        d_colors = {}
        if sbgnml_render_information.list_of_color_definitions is not None:
            for (
                color_definition
            ) in (
                sbgnml_render_information.list_of_color_definitions.color_definition
            ):
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
                for id in style.id_list.split(" "):
                    layout_element = sbgnml_id_to_layout_element.get(id)
                    if layout_element is not None:
                        if momapy.builder.isinstance_or_builder(
                            layout_element, momapy.sbgn.core.SBGNNode
                        ):
                            node_ids.append(id)
                        else:
                            arc_ids.append(id)
                if node_ids:
                    node_style_collection = momapy.styling.StyleCollection()
                    for attr in ["fill", "stroke"]:
                        color_str = getattr(style.g, attr)
                        if color_str is not None:
                            color = d_colors.get(color_str)
                            if color is None:
                                color = momapy.coloring.Color.from_hex(
                                    color_str
                                )
                            node_style_collection[f"border_{attr}"] = color
                    for attr in ["stroke_width"]:
                        value = getattr(style.g, attr)
                        if value is not None:
                            node_style_collection[f"border_{attr}"] = value
                    if node_style_collection:
                        node_selector = momapy.styling.OrSelector(
                            tuple(
                                [
                                    momapy.styling.IdSelector(id)
                                    for id in node_ids
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
                                color = momapy.coloring.Color.from_hex(
                                    color_str
                                )
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
                            tuple(
                                [
                                    momapy.styling.IdSelector(id)
                                    for id in arc_ids
                                ]
                            )
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
                                momapy.core.TextLayout.__name__
                            ),
                        )
                        style_sheet[node_label_selector] = (
                            label_style_collection
                        )
                    if arc_ids:
                        arc_label_selector = momapy.styling.ChildSelector(
                            arc_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.TextLayout.__name__
                            ),
                        )
                        style_sheet[arc_label_selector] = (
                            label_style_collection
                        )
        return style_sheet

    @classmethod
    def _annotations_from_sbgnml(cls, map_, annotation_element):
        annotations = []
        if annotation_element.rdf is not None:
            if annotation_element.rdf.description is not None:
                for (
                    qualifier_attribute
                ) in cls._SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER:
                    annotation_values = getattr(
                        annotation_element.rdf.description, qualifier_attribute
                    )
                    if annotation_values:
                        for annotation_value in annotation_values:
                            annotation_bag = annotation_value.bag
                            for li in annotation_bag.li:
                                resource = li.resource
                                annotation = map_.new_model_element(
                                    momapy.sbgn.core.Annotation
                                )
                                annotation.qualifier = cls._SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER[
                                    qualifier_attribute
                                ]
                                annotation.resource = resource
                                annotations.append(annotation)
        return annotations

    @classmethod
    def _notes_from_sbgnml(cls, notes_element):
        config = xsdata.formats.dataclass.serializers.config.SerializerConfig(
            pretty_print=True
        )
        serializer = xsdata.formats.dataclass.serializers.XmlSerializer(
            config=config
        )
        notes = serializer.render(
            notes_element,
        )
        notes = "\n".join(notes.split("\n")[2:-2])
        return notes

    @classmethod
    def _get_module_from_map(cls, map_):
        if momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.pd.SBGNPDMap
        ):
            return momapy.sbgn.pd
        else:
            return momapy.sbgn.af


class SBGNML0_2Reader(_SBGNMLReader):
    _parser_module = momapy.sbgn.io._sbgnml_parser_0_2

    @classmethod
    @abc.abstractmethod
    def _get_sbgnml_map_from_sbgnml(cls, sbgnml_sbgn):
        return sbgnml_sbgn.map

    @classmethod
    @abc.abstractmethod
    def _make_map_no_subelements_from_sbgnml(cls, sbgnml_map):
        if sbgnml_map.language.name == "PROCESS_DESCRIPTION":
            map_ = momapy.sbgn.pd.SBGNPDMapBuilder()
        elif sbgnml_map.language.name == "ACTIVITY_FLOW":
            map_ = momapy.sbgn.af.SBGNAFMapBuilder()
        elif sbgnml_map.language.name == "ENTITY_RELATIONSHIP":
            raise TypeError("entity relationship maps are not yet supported")
        else:
            raise TypeError(f"unknown language {sbgnml_map.language.value}")
        map_.model = map_.new_model()
        map_.layout = map_.new_layout()
        map_.layout_model_mapping = map_.new_layout_model_mapping()
        return map_

    @classmethod
    def check_file(cls, file_path):
        with open(file_path) as f:
            for line in f:
                if "sbgn" in line and "http://sbgn.org/libsbgn/0.2" in line:
                    return True
        return False


class SBGNML0_3Reader(_SBGNMLReader):
    _parser_module = momapy.sbgn.io._sbgnml_parser_0_3
    _SBGNML_VERSION_URI_TO_MAP_CLASS = {
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_2_0": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_3": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_2": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_1": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_0": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_2": momapy.sbgn.pd.SBGNPDMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_2": None,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_1": None,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_0": None,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1": None,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1_2": momapy.sbgn.af.SBGNAFMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1_0": momapy.sbgn.af.SBGNAFMapBuilder,
        "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1": momapy.sbgn.af.SBGNAFMapBuilder,
    }

    @classmethod
    @abc.abstractmethod
    def _get_sbgnml_map_from_sbgnml(cls, sbgnml_sbgn):
        sbgnml_map = sbgnml_sbgn.map[0]
        return sbgnml_map

    @classmethod
    def _make_map_no_subelements_from_sbgnml(cls, sbgnml_map):
        if sbgnml_map.version is not None:
            map_cls = cls._SBGNML_VERSION_URI_TO_MAP_CLASS[
                sbgnml_map.version.name
            ]
            if map_cls is None:
                raise TypeError(
                    "entity relationship maps are not yet supported"
                )
        else:
            if sbgnml_map.language.name == "PROCESS_DESCRIPTION":
                map_cls = momapy.sbgn.pd.SBGNPDMapBuilder
            elif sbgnml_map.language.name == "ACTIVITY_FLOW":
                map_cls = momapy.sbgn.af.SBGNAFMapBuilder
            elif sbgnml_map.language.name == "ENTITY_RELATIONSHIP":
                raise TypeError(
                    "entity relationship maps are not yet supported"
                )
            else:
                raise TypeError(
                    f"unknown language {sbgnml_map.language.value}"
                )
        map_ = map_cls()
        map_.model = map_.new_model()
        map_.layout = map_.new_layout()
        map_.layout_model_mapping = map_.new_layout_model_mapping()
        map_.id = sbgnml_map.id
        return map_

    @classmethod
    def check_file(cls, file_path):
        with open(file_path) as f:
            for line in f:
                if "sbgn" in line and "http://sbgn.org/libsbgn/0.3" in line:
                    return True
        return False


class _SBGNMLWriter(momapy.io.MapWriter):
    _SBGN_CLASS_TO_TRANSFORMATION_FUNC = {
        momapy.sbgn.pd.CompartmentLayout: "_compartment_to_glyph",
        momapy.sbgn.pd.SubmapLayout: "_submap_to_glyph",
        momapy.sbgn.pd.UnspecifiedEntityLayout: "_unspecified_entity_to_glyph",
        momapy.sbgn.pd.MacromoleculeLayout: "_macromolecule_to_glyph",
        momapy.sbgn.pd.SimpleChemicalLayout: "_simple_chemical_to_glyph",
        momapy.sbgn.pd.NucleicAcidFeatureLayout: "_nucleic_acid_feature_to_glyph",
        momapy.sbgn.pd.ComplexLayout: "_complex_to_glyph",
        momapy.sbgn.pd.MacromoleculeMultimerLayout: "_macromolecule_multimer_to_glyph",
        momapy.sbgn.pd.SimpleChemicalMultimerLayout: "_simple_chemical_multimer_to_glyph",
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout: "_nucleic_acid_feature_multimer_to_glyph",
        momapy.sbgn.pd.ComplexMultimerLayout: "_complex_multimer_to_glyph",
        momapy.sbgn.pd.PerturbingAgentLayout: "_perturbing_agent_to_glyph",
        momapy.sbgn.pd.EmptySetLayout: "_empty_set_to_glyph",
        momapy.sbgn.pd.StateVariableLayout: "_state_variable_to_glyph",
        momapy.sbgn.pd.UnitOfInformationLayout: "_unit_of_information_to_glyph",
        momapy.sbgn.pd.TerminalLayout: "_terminal_to_glyph",
        momapy.sbgn.pd.TagLayout: "_tag_to_glyph",
        momapy.sbgn.pd.GenericProcessLayout: "_generic_process_to_glyph",
        momapy.sbgn.pd.UncertainProcessLayout: "_uncertain_process_to_glyph",
        momapy.sbgn.pd.OmittedProcessLayout: "_omitted_process_to_glyph",
        momapy.sbgn.pd.AssociationLayout: "_association_to_glyph",
        momapy.sbgn.pd.DissociationLayout: "_dissociation_to_glyph",
        momapy.sbgn.pd.PhenotypeLayout: "_phenotype_to_glyph",
        momapy.sbgn.pd.AndOperatorLayout: "_and_operator_to_glyph",
        momapy.sbgn.pd.OrOperatorLayout: "_or_operator_to_glyph",
        momapy.sbgn.pd.NotOperatorLayout: "_not_operator_to_glyph",
        momapy.sbgn.pd.EquivalenceOperatorLayout: "_equivalence_operator_to_glyph",
        momapy.sbgn.pd.ConsumptionLayout: "_consumption_to_arc",
        momapy.sbgn.pd.ProductionLayout: "_production_to_arc",
        momapy.sbgn.pd.ModulationLayout: "_modulation_to_arc",
        momapy.sbgn.pd.StimulationLayout: "_stimulation_to_arc",
        momapy.sbgn.pd.CatalysisLayout: "_catalysis_to_arc",
        momapy.sbgn.pd.NecessaryStimulationLayout: "_necessary_stimulation_to_arc",
        momapy.sbgn.pd.InhibitionLayout: "_inhibition_to_arc",
        momapy.sbgn.pd.LogicArcLayout: "_logic_arc_to_arc",
        momapy.sbgn.pd.EquivalenceArcLayout: "_equivalence_arc_to_arc",
        momapy.sbgn.af.CompartmentLayout: "_compartment_to_glyph",
        momapy.sbgn.af.SubmapLayout: "_submap_to_glyph",
        momapy.sbgn.af.BiologicalActivityLayout: "_biological_activity_to_glyph",
        momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout: "_unit_of_information_unspecified_entity_to_glyph",
        momapy.sbgn.af.MacromoleculeUnitOfInformationLayout: "_unit_of_information_macromolecule_to_glyph",
        momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout: "_unit_of_information_simple_chemical_to_glyph",
        momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout: "_unit_of_information_nucleic_acid_feature_to_glyph",
        momapy.sbgn.af.ComplexUnitOfInformationLayout: "_unit_of_information_complex_to_glyph",
        momapy.sbgn.af.PerturbationUnitOfInformationLayout: "_unit_of_information_perturbation_to_glyph",
        momapy.sbgn.af.PhenotypeLayout: "_phenotype_to_glyph",
        momapy.sbgn.af.AndOperatorLayout: "_and_operator_to_glyph",
        momapy.sbgn.af.OrOperatorLayout: "_or_operator_to_glyph",
        momapy.sbgn.af.NotOperatorLayout: "_not_operator_to_glyph",
        momapy.sbgn.af.DelayOperatorLayout: "_delay_operator_to_glyph",
        momapy.sbgn.af.UnknownInfluenceLayout: "_unknown_influence_to_arc",
        momapy.sbgn.af.PositiveInfluenceLayout: "_positive_influence_to_arc",
        momapy.sbgn.af.NecessaryStimulationLayout: "_necessary_stimulation_to_arc",
        momapy.sbgn.af.NegativeInfluenceLayout: "_negative_influence_to_arc",
        momapy.sbgn.af.TerminalLayout: "_terminal_to_glyph",
        momapy.sbgn.af.TagLayout: "_tag_to_glyph",
        momapy.sbgn.af.LogicArcLayout: "_logic_arc_to_arc",
        momapy.sbgn.af.EquivalenceArcLayout: "_equivalence_arc_to_arc",
    }
    _SBGN_QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE = {
        momapy.sbgn.core.BQBiol.ENCODES: (
            "encodes",
            "Encodes",
        ),
        momapy.sbgn.core.BQBiol.HAS_PART: (
            "has_part",
            "HasPart",
        ),
        momapy.sbgn.core.BQBiol.HAS_PROPERTY: (
            "has_property",
            "HasProperty",
        ),
        momapy.sbgn.core.BQBiol.HAS_VERSION: (
            "has_version",
            "HasVersion",
        ),
        momapy.sbgn.core.BQBiol.IS: (
            "is_value",
            "Is1",
        ),
        momapy.sbgn.core.BQBiol.IS_DESCRIBED_BY: (
            "is_described_by",
            "IsDescribedBy1",
        ),
        momapy.sbgn.core.BQBiol.IS_ENCODED_BY: (
            "is_encoded_by",
            "IsEncodedBy",
        ),
        momapy.sbgn.core.BQBiol.IS_HOMOLOG_TO: (
            "is_homolog_to",
            "IsHomologTo",
        ),
        momapy.sbgn.core.BQBiol.IS_PART_OF: (
            "is_part_of",
            "IsPartOf",
        ),
        momapy.sbgn.core.BQBiol.IS_PROPERTY_OF: (
            "is_property_of",
            "IsPropertyOf",
        ),
        momapy.sbgn.core.BQBiol.IS_VERSION_OF: (
            "is_version_of",
            "IsVersionOf",
        ),
        momapy.sbgn.core.BQBiol.OCCURS_IN: (
            "occurs_in",
            "OccursIn",
        ),
        momapy.sbgn.core.BQBiol.HAS_TAXON: (
            "has_taxon",
            "HasTaxon",
        ),
        momapy.sbgn.core.BQModel.HAS_INSTANCE: (
            "has_instance",
            "HasInstance",
        ),
        momapy.sbgn.core.BQModel.IS: (
            "biomodels_net_model_qualifiers_is",
            "Is2",
        ),
        momapy.sbgn.core.BQModel.IS_DERIVED_FROM: (
            "is_derived_from",
            "IsDerivedFrom",
        ),
        momapy.sbgn.core.BQModel.IS_DESCRIBED_BY: (
            "biomodels_net_model_qualifiers_is_described_by",
            "IsDescribedBy2",
        ),
        momapy.sbgn.core.BQModel.IS_INSTANCE_OF: (
            "is_instance_of",
            "IsInstanceOf",
        ),
    }
    _parser_module = None

    @classmethod
    def write(
        cls,
        map_,
        file_path,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        sbgn = cls._sbgn_from_map(
            map_,
            with_render_information=with_render_information,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        config = xsdata.formats.dataclass.serializers.config.SerializerConfig(
            pretty_print=True
        )
        serializer = xsdata.formats.dataclass.serializers.XmlSerializer(
            config=config
        )
        xml = serializer.render(
            sbgn,
            ns_map={
                "sbgn": cls._parser_module.Sbgn.Meta.namespace,
                "render": "http://www.sbml.org/sbml/level3/version1/render/version1",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "bqbiol": "http://biomodels.net/biology-qualifiers/",
                "bqmodel": "http://biomodels.net/model-qualifiers/",
            },
        )
        # for notes since processContents=strict is not currently taken into account
        xml = xml.replace("&lt;", "<")
        xml = xml.replace("&gt;", ">")
        with open(file_path, "w") as f:
            f.write(xml)

    @classmethod
    @abc.abstractmethod
    def _sbgn_objs_from_map(cls, map_):
        return NotImplemented

    @classmethod
    def _sbgn_from_map(
        cls,
        map_,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        sbgn, sbgn_map = cls._sbgn_objs_from_map(map_)
        dstyles = {}
        for layout_element in map_.layout.layout_elements:
            sbgn_elements = cls._sbgn_elements_from_layout_element(
                layout_element,
                map_,
                dstyles,
                map_.layout,
                with_annotations,
                with_notes,
            )
            for sbgn_element in sbgn_elements:
                cls._add_sub_sbgn_element_to_sbgn_element(
                    sbgn_element, sbgn_map
                )
        bbox = cls._parser_module.Bbox()
        bbox.x = map_.layout.position.x - map_.layout.width / 2
        bbox.y = map_.layout.position.y - map_.layout.height / 2
        bbox.w = map_.layout.width
        bbox.h = map_.layout.height
        sbgn_map.bbox = bbox
        if with_render_information:
            render_information = cls._render_information_from_styles(dstyles)
            render_information.id = momapy.utils.get_uuid4_as_()
            render_information.program_name = momapy.__about__.__name__
            render_information.program_version = momapy.__about__.__version__
            render_information.background_color = map_.layout.fill.to_hexa()
            extension = cls._parser_module.Map.Extension()
            extension.render_information = render_information
            sbgn_map.extension = extension
        if with_annotations and len(map_.model.annotations) != 0:
            annotation_sbgn_element = cls._annotation_element_from_annotations(
                map_.model.annotations, model_element.id
            )
            if sbgn_map.extension is None:
                extension = cls._parser_module.Map.Extension()
                sbgn_map.extension = extension
            extension.annotation = annotation_sbgn_element
        if with_notes and map_.notes is not None:
            notes_element = cls._notes_element_from_notes(map_.notes)
            sbgn_map.notes = notes_element
        return sbgn

    @classmethod
    def _sbgn_elements_from_layout_element(
        cls,
        layout_element,
        map_,
        dstyles,
        super_layout_element,
        with_annotations=True,
        with_notes=True,
    ):
        transformation_func = cls._get_transformation_func_from_layout_element(
            layout_element
        )
        if transformation_func is not None:
            sbgn_elements = transformation_func(
                layout_element, map_, dstyles, super_layout_element
            )
            if with_annotations:
                model_element = map_.get_mapping(layout_element, unpack=True)[
                    0
                ]
                if len(model_element.annotations) != 0:
                    annotation_sbgn_element = (
                        cls._annotation_element_from_annotations(
                            model_element.annotations, layout_element.id
                        )
                    )
                    extension = cls._parser_module.Map.Extension()
                    extension.annotation = annotation_sbgn_element
                    sbgn_elements[0].extension = extension
            if with_notes:
                model_element = map_.get_mapping(layout_element, unpack=True)[
                    0
                ]
                if model_element.notes is not None:
                    notes_element = cls._notes_element_from_notes(
                        model_element.notes
                    )
                    sbgn_element[0].notes = notes
        else:
            print(
                f"object {layout_element.id}: unknown class value '{type(layout_element)}' for transformation"
            )
            sbgn_elements = []
        return sbgn_elements

    @classmethod
    def _add_sub_sbgn_element_to_sbgn_element(
        cls, sub_sbgn_element, sbgn_element
    ):
        if isinstance(sub_sbgn_element, cls._parser_module.Glyph):
            sbgn_element.glyph.append(sub_sbgn_element)
        elif isinstance(sub_sbgn_element, cls._parser_module.Arc):
            sbgn_element.arc.append(sub_sbgn_element)
        elif isinstance(sub_sbgn_element, cls._parser_module.Arcgroup):
            sbgn_element.arcgroup.append(sub_sbgn_element)

    @classmethod
    def _get_transformation_func_from_layout_element(cls, layout_element):
        if momapy.builder.isinstance_or_builder(
            layout_element, momapy.builder.Builder
        ):
            layout_element_cls = type(layout_element)._cls_to_build
        else:
            layout_element_cls = type(layout_element)
        transformation_func_name = cls._SBGN_CLASS_TO_TRANSFORMATION_FUNC.get(
            layout_element_cls
        )
        if transformation_func_name is not None:
            return getattr(cls, transformation_func_name)
        else:
            return None

    @classmethod
    def _render_information_from_styles(cls, dstyles):
        dcolors = {}
        render_information = cls._parser_module.RenderInformation()
        list_of_styles = cls._parser_module.ListOfStylesType()
        render_information.list_of_styles = list_of_styles
        list_of_color_definitions = (
            cls._parser_module.ListOfColorDefinitionsType()
        )
        render_information.list_of_color_definitions = (
            list_of_color_definitions
        )
        for style in dstyles:
            for attr in ["stroke", "fill"]:
                if attr in style:
                    color = style[attr]
                    if (
                        color is not None
                        and color is not momapy.drawing.NoneValue
                    ):
                        if color.to_hexa() not in dcolors:
                            dcolors[color.to_hexa()] = (
                                momapy.utils.get_uuid4_as_()
                            )
            sbgn_style = cls._parser_module.StyleType()
            sbgn_style.id = momapy.utils.get_uuid4_as_()
            sbgn_style.id_list = " ".join(dstyles[style])
            sbgn_g = cls._parser_module.GType()
            for attr in ["stroke", "fill"]:
                if (
                    attr in style
                    and style[attr] is not None
                    and style[attr] is not momapy.drawing.NoneValue
                ):
                    setattr(sbgn_g, attr, dcolors[style[attr].to_hexa()])
            for attr in [
                "stroke_width",
                "font_family",
                "font_size",
                "font_color",
            ]:
                if attr in style:
                    setattr(sbgn_g, attr, style[attr])
            sbgn_style.g = sbgn_g
            render_information.list_of_styles.style.append(sbgn_style)
        for color in dcolors:
            color_definition = cls._parser_module.ColorDefinitionType()
            color_definition.id = dcolors[color]
            color_definition.value = color
            render_information.list_of_color_definitions.color_definition.append(
                color_definition
            )
        return render_information

    @classmethod
    def _annotation_element_from_annotations(cls, annotations, element_id):
        annotation_element = cls._parser_module.Annotation()
        rdf = cls._parser_module.Rdf()
        annotation_element.rdf = rdf
        description = cls._parser_module.DescriptionType()
        description.about = element_id
        rdf.description = description
        d_annotations = {}
        for annotation in annotations:
            if annotation.qualifier not in d_annotations:
                d_annotations[annotation.qualifier] = []
            d_annotations[annotation.qualifier].append(annotation.resource)
        for qualifier_member, resources in d_annotations.items():
            (
                qualifier_attribute,
                qualifier_cls_name,
            ) = cls._SBGN_QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
                qualifier_member
            ]
            qualifier_cls = getattr(cls._parser_module, qualifier_cls_name)
            qualifier_element = qualifier_cls()
            bag = cls._parser_module.Bag()
            qualifier_element.bag = bag
            for resource in resources:
                li = cls._parser_module.LiType()
                li.resource = resource
                bag.li.append(li)
            setattr(description, qualifier_attribute, qualifier_element)
        return annotation_element

    @classmethod
    def _notes_element_from_notes(cls, notes):
        notes_element = cls._parser_module.Map.Notes()
        notes_element.w3_org_1999_xhtml_element.append(notes)
        return notes_element

    @classmethod
    def _node_layout_to_sbgn_elements(
        cls,
        layout_element,
        class_value,
        map_,
        dstyles,
        make_label=True,
        make_sub_elements=True,
        add_sub_elements_to_element=True,
        add_sub_elements_to_return=False,
    ):
        sbgn_elements = []
        glyph = cls._parser_module.Glyph()
        glyph.id = layout_element.id
        glyph.class_value = class_value
        bbox = cls._parser_module.Bbox()
        bbox.x = layout_element.x - layout_element.width / 2
        bbox.y = layout_element.y - layout_element.height / 2
        bbox.w = layout_element.width
        bbox.h = layout_element.height
        glyph.bbox = bbox
        if make_label and layout_element.label is not None:
            sbgn_label = cls._parser_module.Label()
            sbgn_label.text = layout_element.label.text
            glyph.label = sbgn_label
            ink_bbox = layout_element.label.ink_bbox()
            label_bbox = cls._parser_module.Bbox()
            label_bbox.x = ink_bbox.x - ink_bbox.width / 2
            label_bbox.y = ink_bbox.y - ink_bbox.height / 2
            label_bbox.w = ink_bbox.width
            label_bbox.h = ink_bbox.height
            sbgn_label.bbox = label_bbox
        sbgn_elements.append(glyph)
        if make_sub_elements:
            for sub_layout_element in layout_element.layout_elements:
                sub_sbgn_elements = cls._sbgn_elements_from_layout_element(
                    sub_layout_element,
                    map_,
                    dstyles,
                    layout_element,
                )
                if add_sub_elements_to_element:
                    for sub_sbgn_element in sub_sbgn_elements:
                        cls._add_sub_sbgn_element_to_sbgn_element(
                            sub_sbgn_element, glyph
                        )
                if add_sub_elements_to_return:
                    sbgn_elements += sub_sbgn_elements

        lattrs = []
        for attr_name in ["fill", "stroke", "stroke_width"]:
            attr_value = getattr(layout_element, f"border_{attr_name}")
            if attr_value is None:
                attr_value = getattr(layout_element, attr_name)
            lattrs.append(
                (
                    attr_name,
                    attr_value,
                )
            )
        if layout_element.label is not None:
            lattrs += [
                ("font_family", layout_element.label.font_family),
                ("font_size", layout_element.label.font_size),
                ("font_color", layout_element.label.fill.to_hex()),
            ]
        style = frozendict.frozendict(lattrs)
        if style not in dstyles:
            dstyles[style] = [glyph.id]
        else:
            dstyles[style].append(glyph.id)
        return sbgn_elements

    @classmethod
    def _entity_node_layout_to_sbgn_elements(
        cls, layout_element, class_value, map_, dstyles
    ):
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        model_element = map_.get_mapping(layout_element, unpack=True)[0]
        if (
            hasattr(model_element, "compartment")
            and model_element.compartment is not None
        ):
            compartment_id = model_element.compartment.id
            glyph.compartment_ref = compartment_id
        return sbgn_elements

    @classmethod
    def _compartment_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.COMPARTMENT
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgn_elements

    @classmethod
    def _submap_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.SUBMAP
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgn_elements

    @classmethod
    def _unspecified_entity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNSPECIFIED_ENTITY
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _macromolecule_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.MACROMOLECULE
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _simple_chemical_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.SIMPLE_CHEMICAL
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _nucleic_acid_feature_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.NUCLEIC_ACID_FEATURE
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _complex_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.COMPLEX
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _macromolecule_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.MACROMOLECULE_MULTIMER
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _simple_chemical_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.SIMPLE_CHEMICAL_MULTIMER
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _nucleic_acid_feature_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            cls._parser_module.GlyphClass.NUCLEIC_ACID_FEATURE_MULTIMER
        )
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _complex_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.COMPLEX_MULTIMER
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _perturbing_agent_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.PERTURBING_AGENT
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _empty_set_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.SOURCE_AND_SINK
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _biological_activity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.BIOLOGICAL_ACTIVITY
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _auxiliary_unit_layout_to_sbgn_elements(
        cls, layout_element, class_value, map_, dstyles, super_layout_element
    ):
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=False,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgn_elements

    @classmethod
    def _state_variable_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.STATE_VARIABLE
        sbgn_elements = cls._auxiliary_unit_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            super_layout_element,
        )
        glyph = sbgn_elements[0]
        state_variable = map_.get_mapping(layout_element, unpack=True)[0]
        sbgn_state = cls._parser_module.Glyph.State()
        sbgn_state.value = state_variable.value
        sbgn_state.variable = (
            state_variable.variable
            if not momapy.builder.isinstance_or_builder(
                state_variable.variable, momapy.sbgn.pd.UndefinedVariable
            )
            else None
        )
        glyph.state = sbgn_state
        return sbgn_elements

    @classmethod
    def _unit_of_information_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_unspecified_entity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.UNSPECIFIED_ENTITY
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_macromolecule_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.MACROMOLECULE
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_simple_chemical_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.SIMPLE_CHEMICAL
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_nucleic_acid_feature_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.NUCLEIC_ACID_FEATURE
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_complex_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.COMPLEX
        )
        return sbgn_elements

    @classmethod
    def _unit_of_information_perturbation_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNIT_OF_INFORMATION
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgn_elements[0]
        glyph.entity = cls._parser_module.Glyph.Entity(
            name=cls._parser_module.EntityName.PERTURBATION
        )
        return sbgn_elements

    @classmethod
    def _terminal_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.TERMINAL
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        return sbgn_elements

    @classmethod
    def _tag_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.TAG
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        return sbgn_elements

    @classmethod
    def _process_node_layout_to_sbgn_elements(
        cls,
        layout_element,
        class_value,
        map_,
        dstyles,
    ):
        sbgn_elements = cls._node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        glyph = sbgn_elements[0]
        if layout_element.direction == momapy.core.Direction.HORIZONTAL:
            glyph.orientation = cls._parser_module.GlyphOrientation.HORIZONTAL
        else:
            glyph.orientation = cls._parser_module.GlyphOrientation.VERTICAL
        left_port = cls._parser_module.Port()
        left_port.id = f"{layout_element.id}_left_port"
        left_connector_tip = layout_element.left_connector_tip()
        left_port.x = left_connector_tip.x
        left_port.y = left_connector_tip.y
        glyph.port.append(left_port)
        right_port = cls._parser_module.Port()
        right_port.id = f"{layout_element.id}_right_port"
        right_connector_tip = layout_element.right_connector_tip()
        right_port.x = right_connector_tip.x
        right_port.y = right_connector_tip.y
        glyph.port.append(right_port)
        return sbgn_elements

    @classmethod
    def _generic_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.PROCESS
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _uncertain_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.UNCERTAIN_PROCESS
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _omitted_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.OMITTED_PROCESS
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _association_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.ASSOCIATION
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _dissociation_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.DISSOCIATION
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _phenotype_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.PHENOTYPE
        sbgn_elements = cls._entity_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgn_elements

    @classmethod
    def _and_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.AND
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _or_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.OR
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _not_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.NOT
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _equivalence_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.EQUIVALENCE
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _delay_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.GlyphClass.DELAY
        sbgn_elements = cls._process_node_layout_to_sbgn_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgn_elements

    @classmethod
    def _arc_layout_to_sbgn_elements(
        cls,
        layout_element,
        class_value,
        source_id,
        target_id,
        dstyles,
        reverse_points_order=False,
    ):
        sbgn_elements = []
        arc = cls._parser_module.Arc()
        arc.class_value = class_value
        arc.id = layout_element.id
        points = layout_element.points()
        if reverse_points_order:
            start_point = points[-1]
            end_point = points[0]
        else:
            start_point = points[0]
            end_point = points[-1]
        start = cls._parser_module.Arc.Start()
        start.x = start_point.x
        start.y = start_point.y
        arc.start = start
        end = cls._parser_module.Arc.End()
        end.x = end_point.x
        end.y = end_point.y
        arc.end = end
        arc.source = source_id
        arc.target = target_id
        sbgn_elements.append(arc)
        for sub_layout_element in layout_element.layout_elements:
            sub_sbgn_elements = cls._sbgn_elements_from_layout_element(
                sub_layout_element,
                map_,
                layout_element,
            )
            for sub_sbgn_element in sub_sbgn_elements:
                cls._add_sub_sbgn_element_to_sbgn_element(
                    sub_sbgn_element, arc
                )
        lattrs = []
        for attr_name in ["fill", "stroke", "stroke_width"]:
            attr_value = getattr(layout_element, f"arrowhead_{attr_name}")
            if attr_value is None:
                if attr_name != "fill":
                    attr_value = getattr(layout_element, f"path_{attr_name}")
                if attr_value is None:
                    attr_value = getattr(layout_element, attr_name)
            lattrs.append(
                (
                    attr_name,
                    attr_value,
                )
            )
        style = frozendict.frozendict(lattrs)
        if style not in dstyles:
            dstyles[style] = [arc.id]
        else:
            dstyles[style].append(arc.id)
        return sbgn_elements

    @classmethod
    def _consumption_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.CONSUMPTION
        source_id = layout_element.target.id
        if super_layout_element.left_to_right:
            target_id = f"{super_layout_element.id}_left_port"
        else:
            target_id = f"{super_layout_element.id}_right_port"
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgn_elements

    @classmethod
    def _production_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.PRODUCTION
        target_id = layout_element.target.id
        if super_layout_element.left_to_right:
            source_id = f"{super_layout_element.id}_right_port"
        else:
            source_id = f"{super_layout_element.id}_left_port"
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _modulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.MODULATION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _stimulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.STIMULATION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _necessary_stimulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.NECESSARY_STIMULATION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _catalysis_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.CATALYSIS
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _inhibition_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.INHIBITION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _unknown_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.UNKNOWN_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _positive_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.POSITIVE_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _negative_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.NEGATIVE_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgn_elements

    @classmethod
    def _logic_arc_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.LOGIC_ARC
        source_id = layout_element.target.id
        if super_layout_element.left_to_right:
            target_id = f"{super_layout_element.id}_left_port"
        else:
            target_id = f"{super_layout_element.id}_right_port"
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgn_elements

    @classmethod
    def _equivalence_arc_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = cls._parser_module.ArcClass.EQUIVALENCE_ARC
        source_id = layout_element.target.id
        target_id = super_layout_element.id
        sbgn_elements = cls._arc_layout_to_sbgn_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgn_elements


class SBGNML0_2Writer(_SBGNMLWriter):
    _parser_module = momapy.sbgn.io._sbgnml_parser_0_2

    @classmethod
    def _sbgn_objs_from_map(cls, map_):
        sbgn = cls._parser_module.Sbgn()
        sbgn_map = cls._parser_module.Map()
        if momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.pd.SBGNPDMap
        ):
            sbgn_language = cls._parser_module.MapLanguage.PROCESS_DESCRIPTION
        elif momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.af.SBGNAFMap
        ):
            sbgn_language = cls._parser_module.MapLanguage.ACTIVITY_FLOW
        else:
            raise TypeError("this type of map is not yet supported")
        sbgn_map_.language = sbgn_language
        sbgn.map = sbgn_map
        return sbgn, sbgn_map


class SBGNML0_3Writer(_SBGNMLWriter):
    _parser_module = momapy.sbgn.io._sbgnml_parser_0_3

    @classmethod
    def _sbgn_objs_from_map(cls, map_):
        sbgn = cls._parser_module.Sbgn()
        sbgn_map = cls._parser_module.Map()
        sbgn_map_.id = map_.id
        if momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.pd.SBGNPDMap
        ):
            sbgn_language = cls._parser_module.MapLanguage.PROCESS_DESCRIPTION
        elif momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.af.SBGNAFMap
        ):
            sbgn_language = cls._parser_module.MapLanguage.ACTIVITY_FLOW
        else:
            raise TypeError("this type of map is not yet supported")
        sbgn_map_.language = sbgn_language
        if sbgn_language.name == "PROCESS_DESCRIPTION":
            sbgn_version = cls._parser_module.MapVersion[
                "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_2_0"
            ]
        elif sbgn_language == "ACTIVITY_FLOW":
            sbgn_version = cls._parser_module.MapVersion[
                "HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1_2"
            ]
        sbgn_map.version = sbgn_version
        sbgn.map.append(sbgn_map)
        return sbgn, sbgn_map


momapy.io.register_reader("sbgnml-0.2", SBGNML0_2Reader)
momapy.io.register_reader("sbgnml-0.3", SBGNML0_3Reader)
momapy.io.register_reader("sbgnml", SBGNML0_3Reader)
momapy.io.register_writer("sbgnml-0.2", SBGNML0_2Writer)
momapy.io.register_writer("sbgnml-0.3", SBGNML0_3Writer)
momapy.io.register_writer("sbgnml", SBGNML0_3Writer)
