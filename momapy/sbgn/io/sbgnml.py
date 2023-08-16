import uuid

import frozendict

import xsdata.formats.dataclass.context
import xsdata.formats.dataclass.parsers
import xsdata.formats.dataclass.parsers.config
import xsdata.formats.dataclass.serializers
import xsdata.formats.dataclass.serializers.config

import momapy.__about__
import momapy.core
import momapy.io
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.styling
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.io._sbgnml_parser


class SBGNMLReader(momapy.io.MapReader):
    _DEFAULT_FONT_FAMILY = "Helvetica"
    _DEFAULT_FONT_SIZE = 14.0
    _DEFAULT_FONT_COLOR = momapy.coloring.black
    _SBGNML_ELEMENT_CLASS_TO_TRANSFORMATION_FUNC_MAPPING = {
        "COMPARTMENT": "_compartment_elements_from_glyph",
        "SUBMAP": "_submap_elements_from_glyph",
        "BIOLOGICAL_ACTIVITY": "_biological_activity_from_glyph",
        "UNSPECIFIED_ENTITY": "_unspecified_entity_elements_from_glyph",
        "MACROMOLECULE": "_macromolecule_elements_from_glyph",
        "MACROMOLECULE_MULTIMER": "_macromolecule_multimer_elements_from_glyph",
        "SIMPLE_CHEMICAL": "_simple_chemical_elements_from_glyph",
        "SIMPLE_CHEMICAL_MULTIMER": "_simple_chemical_multimer_elements_from_glyph",
        "NUCLEIC_ACID_FEATURE": "_nucleic_acid_feature_elements_from_glyph",
        "NUCLEIC_ACID_FEATURE_MULTIMER": "_nucleic_acid_feature_multimer_elements_from_glyph",
        "COMPLEX": "_complex_elements_from_glyph",
        "COMPLEX_MULTIMER": "_complex_multimer_elements_from_glyph",
        "SOURCE_AND_SINK": "_empty_set_elements_from_glyph",
        "PERTURBING_AGENT": "_perturbing_agent_elements_from_glyph",
        "PROCESS": "_generic_process_elements_from_glyph",
        "ASSOCIATION": "_association_elements_from_glyph",
        "DISSOCIATION": "_dissociation_elements_from_glyph",
        "UNCERTAIN_PROCESS": "_uncertain_process_elements_from_glyph",
        "OMITTED_PROCESS": "_omitted_process_elements_from_glyph",
        "PHENOTYPE": "_phenotype_elements_from_glyph",
        "STATE_VARIABLE": "_state_variable_elements_from_glyph",
        "UNIT_OF_INFORMATION": "_unit_of_information_elements_from_glyph",
        "UNIT_OF_INFORMATION_UNSPECIFIED_ENTITY": "_unit_of_information_unspecified_entity_elements_from_glyph",
        "UNIT_OF_INFORMATION_MACROMOLECULE": "_unit_of_information_macromolecule_elements_from_glyph",
        "UNIT_OF_INFORMATION_SIMPLE_CHEMICAL": "_unit_of_information_simple_chemical_elements_from_glyph",
        "UNIT_OF_INFORMATION_NUCLEIC_ACID_FEATURE": "_unit_of_information_nucleic_acid_feature_elements_from_glyph",
        "UNIT_OF_INFORMATION_COMPLEX": "_unit_of_information_complex_elements_from_glyph",
        "UNIT_OF_INFORMATION_PERTURBATION": "_unit_of_information_perturbation_elements_from_glyph",
        "TERMINAL": "_terminal_elements_from_glyph",
        "TAG": "_tag_elements_from_glyph",
        "UNSPECIFIED_ENTITY_SUBUNIT": "_unspecified_entity_subunit_elements_from_glyph",
        "MACROMOLECULE_SUBUNIT": "_macromolecule_subunit_elements_from_glyph",
        "MACROMOLECULE_MULTIMER_SUBUNIT": "_macromolecule_multimer_subunit_elements_from_glyph",
        "SIMPLE_CHEMICAL_SUBUNIT": "_simple_chemical_subunit_elements_from_glyph",
        "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT": "_simple_chemical_multimer_subunit_elements_from_glyph",
        "NUCLEIC_ACID_FEATURE_SUBUNIT": "_nucleic_acid_feature_subunit_elements_from_glyph",
        "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT": "_nucleic_acid_feature_multimer_subunit_elements_from_glyph",
        "COMPLEX_SUBUNIT": "_complex_subunit_elements_from_glyph",
        "COMPLEX_MULTIMER_SUBUNIT": "_complex_multimer_subunit_elements_from_glyph",
        "AND": "_and_operator_elements_from_glyph",
        "OR": "_or_operator_elements_from_glyph",
        "NOT": "_not_operator_elements_from_glyph",
        "DELAY": "_delay_operator_elements_from_glyph",
        "CONSUMPTION": "_consumption_elements_from_arc",
        "PRODUCTION": "_production_elements_from_arc",
        "MODULATION": "_modulation_elements_from_arc",
        "STIMULATION": "_stimulation_elements_from_arc",
        "CATALYSIS": "_catalysis_elements_from_arc",
        "NECESSARY_STIMULATION": "_necessary_stimulation_elements_from_arc",
        "INHIBITION": "_inhibition_elements_from_arc",
        "POSITIVE_INFLUENCE": "_positive_influence_elements_from_arc",
        "NEGATIVE_INFLUENCE": "_negative_influence_elements_from_arc",
        "UNKNOWN_INFLUENCE": "_unknown_influence_elements_from_arc",
        "LOGIC_ARC": "_logical_arc_elements_from_arc",
        "EQUIVALENCE_ARC": "_equivalence_arc_elements_from_arc",
    }
    _SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER_MAPPING = {
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

    @classmethod
    def read(
        cls, file_path, with_render_information=True, return_builder=False
    ):
        config = xsdata.formats.dataclass.parsers.config.ParserConfig(
            fail_on_unknown_properties=False
        )
        parser = xsdata.formats.dataclass.parsers.XmlParser(
            config=config, context=xsdata.formats.dataclass.context.XmlContext()
        )
        sbgn = parser.parse(file_path, momapy.sbgn.io._sbgnml_parser.Sbgn)
        sbgn_map = sbgn.map
        map_ = cls._map_from_sbgn_map(sbgn_map)
        if sbgn_map.extension is not None:
            if (
                with_render_information
                and sbgn_map.extension.render_information is not None
            ):
                style_sheet = cls._style_sheet_from_render_information(
                    sbgn_map.extension.render_information, map_
                )
                momapy.styling.apply_style_sheet(map_.layout, style_sheet)
            if sbgn_map.extension.annotation is not None:
                annotations = cls._annotations_from_annotation_element(
                    sbgn_map.extension.annotation, map_
                )
                for annotation in annotations:
                    model_element.add_element(annotation)

        if not return_builder:
            map_ = momapy.builder.object_from_builder(map_)
        return map_

    @classmethod
    def _get_module_from_map(cls, map_):
        if momapy.builder.isinstance_or_builder(map_, momapy.sbgn.pd.SBGNPDMap):
            return momapy.sbgn.pd
        else:
            return momapy.sbgn.af

    @classmethod
    def _is_process_layout_left_to_right(cls, layout_element):
        consumption_layout = None
        production_layout = None
        for sub_layout_element in layout_element.layout_elements:
            if momapy.builder.isinstance_or_builder(
                sub_layout_element, (momapy.sbgn.pd.ConsumptionLayout)
            ):
                consumption_layout = sub_layout_element
            elif momapy.builder.isinstance_or_builder(
                sub_layout_element, (momapy.sbgn.pd.ProductionLayout)
            ):
                production_layout = sub_layout_element
            if consumption_layout is not None and production_layout is not None:
                break
        if consumption_layout is not None and production_layout is not None:
            if layout_element.direction == momapy.core.Direction.HORIZONTAL:
                if (
                    consumption_layout.points()[-1].x
                    < production_layout.points()[-1].x
                ):
                    return True
                else:
                    return False
            else:
                if (
                    consumption_layout.points()[-1].y
                    < production_layout.points()[-1].y
                ):
                    return True
                else:
                    return False
        return True

    @classmethod
    def _is_operator_layout_left_to_right(cls, layout_element):
        for sub_layout_element in layout_element.layout_elements:
            if momapy.builder.isinstance_or_builder(
                sub_layout_element,
                (momapy.sbgn.pd.LogicArcLayout, momapy.sbgn.af.LogicArcLayout),
            ):
                if layout_element.direction == momapy.core.Direction.HORIZONTAL:
                    if sub_layout_element.points()[-1].x < layout_element.x:
                        return True
                    else:
                        return False
                else:
                    if sub_layout_element.points()[-1].y < layout_element.y:
                        return True
                    else:
                        return False
        return True

    @classmethod
    def _map_from_sbgn_map(cls, sbgn_map):
        if sbgn_map.language.name == "PROCESS_DESCRIPTION":
            map_ = momapy.sbgn.pd.SBGNPDMapBuilder()
        elif sbgn_map.language.name == "ACTIVITY_FLOW":
            map_ = momapy.sbgn.af.SBGNAFMapBuilder()
        elif sbgn_map.language.name == "ENTITY_RELATIONSHIP":
            raise TypeError("entity relationship maps are not yet supported")
        else:
            raise TypeError(f"unknown language {sbgn_map.language.value}")
        map_.model = map_.new_model()
        map_.layout = map_.new_layout()
        map_.layout_model_mapping = map_.new_layout_model_mapping()
        d_model_element_ids = {}
        d_layout_element_ids = {}
        for glyph in sbgn_map.glyph:
            (
                model_element,
                layout_element,
            ) = cls._map_elements_from_sbgnml_element(
                glyph,
                map_,
                d_model_element_ids,
                d_layout_element_ids,
                map_.model,
                map_.layout,
            )
        d_processes = {}
        sbgnml_flux_arcs = []
        for arc in sbgn_map.arc:
            # We collect flux arcs to set the reversibility of the processes
            # they belong to. A process is reversible if it only has production
            # arcs.
            if arc.class_value.name == "CONSUMPTION":
                process = d_model_element_ids[arc.target]
                d_processes[process] = False
                sbgnml_flux_arcs.append(arc)
            elif arc.class_value.name == "PRODUCTION":
                process = d_model_element_ids[arc.source]
                if process not in d_processes:
                    d_processes[process] = True
                sbgnml_flux_arcs.append(arc)
            # If the arc is not a flux arc, we transform it immediately. If it
            # is a flux arc, we transform it after we set the reversibily of the
            # processes.
            else:
                (
                    model_element,
                    layout_element,
                ) = cls._map_elements_from_sbgnml_element(
                    arc,
                    map_,
                    d_model_element_ids,
                    d_layout_element_ids,
                    map_.model,
                    map_.layout,
                )
        # We set the reversibility of the processes.
        for process in d_processes:
            process.reversible = d_processes[process]
        # We transform the flux arcs we collected previously.
        for arc in sbgnml_flux_arcs:
            (
                model_element,
                layout_element,
            ) = cls._map_elements_from_sbgnml_element(
                arc,
                map_,
                d_model_element_ids,
                d_layout_element_ids,
                map_.model,
                map_.layout,
            )
        if sbgn_map.language.name == "PROCESS_DESCRIPTION":
            # We set the direction (left-to-right or right-to-left) of the process
            # layouts. By default, process layouts are left-to-right.
            for process in map_.model.processes:
                for process_layout in map_.get_mapping(process):
                    process_layout, *_ = process_layout
                    process_layout.left_to_right = (
                        cls._is_process_layout_left_to_right(process_layout)
                    )
        # We set the direction (left-to-right or right-to-left) of the logical
        # operator layouts. By default, logical operator layouts are
        # left-to-right.
        for logical_operator in map_.model.logical_operators:
            for logical_operator_layout in map_.get_mapping(logical_operator):
                logical_operator_layout, *_ = logical_operator_layout
                logical_operator_layout.left_to_right = (
                    cls._is_operator_layout_left_to_right(
                        logical_operator_layout
                    )
                )

        if sbgn_map.language.name == "PROCESS_DESCRIPTION":
            # We set the direction (left-to-right or right-to-left) of the equivalence
            # operator layouts. By default, equivalence operator layouts are
            # left-to-right.
            for equivalence_operator in map_.model.equivalence_operators:
                for equivalence_operator_layout in map_.get_mapping(
                    equivalence_operator
                ):
                    (
                        equivalence_operator_layout,
                        *_,
                    ) = equivalence_operator_layout
                    equivalence_operator_layout.left_to_right = (
                        cls._is_operator_layout_left_to_right(
                            equivalence_operator_layout
                        )
                    )
        if sbgn_map.bbox is not None:
            map_.layout.position = momapy.geometry.PointBuilder(
                sbgn_map.bbox.x + sbgn_map.bbox.w / 2,
                sbgn_map.bbox.y + sbgn_map.bbox.h / 2,
            )
            map_.layout.width = sbgn_map.w
            map_.layout.height = sbgn_map.h
        else:
            momapy.positioning.set_fit(map_.layout, map_.layout.layout_elements)
        return map_

    @classmethod
    def _style_sheet_from_render_information(cls, render_information, map_):
        style_sheet = momapy.styling.StyleSheet()
        if render_information.background_color is not None:
            style_collection = momapy.styling.StyleCollection()
            layout_selector = momapy.styling.IdSelector(map_.layout.id)
            style_collection["fill"] = momapy.coloring.Color.from_hexa(
                render_information.background_color
            )
            style_sheet[layout_selector] = style_collection
        style_collection
        d_colors = {}
        for (
            color_definition
        ) in render_information.list_of_color_definitions.color_definition:
            color_hex = color_definition.value
            if len(color_hex) < 8:
                color = momapy.coloring.Color.from_hex(color_hex)
            else:
                color = momapy.coloring.Color.from_hexa(color_hex)
            d_colors[color_definition.id] = color
        for style in render_information.list_of_styles.style:
            selector = momapy.styling.OrSelector(
                tuple(
                    [
                        momapy.styling.IdSelector(id_)
                        for id_ in style.id_list.split(" ")
                    ]
                )
            )
            style_collection = momapy.styling.StyleCollection()
            for attr in ["fill", "stroke"]:
                color_id = getattr(style.g, attr)
                if color_id is not None:
                    style_collection[attr] = d_colors[color_id]
            for attr in ["stroke_width"]:
                value = getattr(style.g, attr)
                if value is not None:
                    style_collection[attr] = value
            style_sheet[selector] = style_collection
            label_selector = momapy.styling.ChildSelector(
                selector,
                momapy.styling.TypeSelector(momapy.core.TextLayout.__name__),
            )
            label_style_collection = momapy.styling.StyleCollection()
            for attr in ["font_size", "font_family"]:
                value = getattr(style.g, attr)
                if value is not None:
                    label_style_collection[attr] = value
            for attr in ["font_color"]:
                color_str = getattr(style.g, attr)
                if color_str is not None:
                    if color_str == "#000":
                        color_str = "#000000"
                    label_style_collection[
                        attr
                    ] = momapy.coloring.Color.from_hex(color_str)
            style_sheet[label_selector] = label_style_collection
        return style_sheet

    @classmethod
    def _annotations_from_annotation_element(cls, annotation_element, map_):
        annotations = []
        if annotation_element.rdf is not None:
            if annotation_element.rdf.description is not None:
                for (
                    qualifier_attribute
                ) in (
                    cls._SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER_MAPPING
                ):
                    annotation_value = getattr(
                        annotation_element.rdf.description, qualifier_attribute
                    )
                    if annotation_value is not None:
                        annotation_bag = annotation_value.bag
                        for li in annotation_bag.li:
                            resource = li.resource
                            annotation = map_.new_model_element(
                                momapy.sbgn.core.Annotation
                            )
                            annotation.qualifier = cls._SBGNML_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER_MAPPING[
                                qualifier_attribute
                            ]
                            annotation.resource = resource
                            annotations.append(annotation)
        return annotations

    @classmethod
    def _get_transformation_func_from_sbgnml_element(
        cls, sbgnml_element, super_model_element=None
    ):
        class_str = sbgnml_element.class_value.name
        if (
            momapy.builder.isinstance_or_builder(
                super_model_element, momapy.sbgn.af.BiologicalActivity
            )
            and class_str == "UNIT_OF_INFORMATION"
        ):
            class_str = f"{class_str}_{sbgnml_element.entity.name.name}"
        elif momapy.builder.isinstance_or_builder(
            super_model_element, momapy.sbgn.pd.Complex
        ) and class_str in [
            "UNSPECIFIED_ENTITY",
            "MACROMOLECULE",
            "MACROMOLECULE_MULTIMER",
            "SIMPLE_CHEMICAL",
            "SIMPLE_CHEMICAL_MULTIMER",
            "NUCLEIC_ACID_FEATURE",
            "NUCLEIC_ACID_FEATURE_MULTIMER",
            "COMPLEX",
            "COMPLEX_MULTIMER",
        ]:
            class_str = f"{class_str}_SUBUNIT"
        elif (
            momapy.builder.isinstance_or_builder(
                super_model_element,
                (momapy.sbgn.pd.Submap, momapy.sbgn.af.Submap),
            )
            and class_str == "TAG"
        ):
            class_str = "TERMINAL"
        return getattr(
            cls,
            cls._SBGNML_ELEMENT_CLASS_TO_TRANSFORMATION_FUNC_MAPPING.get(
                class_str
            ),
        )

    @classmethod
    def _map_elements_from_sbgnml_element(
        cls,
        sbgnml_element,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        transformation_func = cls._get_transformation_func_from_sbgnml_element(
            sbgnml_element, super_model_element
        )
        if transformation_func is not None:
            model_element, layout_element = transformation_func(
                sbgnml_element,
                map_,
                d_model_element_ids,
                d_layout_element_ids,
                super_model_element,
                super_layout_element,
            )
            if (
                sbgnml_element.extension is not None
                and sbgnml_element.extension.annotation is not None
            ):
                annotations = cls._annotations_from_annotation_element(
                    sbgnml_element.extension.annotation, map_
                )
                for annotation in annotations:
                    model_element.add_element(annotation)
        else:
            print(
                f"object {sbgnml_element.id}: unknown class value '{sbgnml_element.class_value}' for transformation"
            )
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _node_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
        make_model_label=True,
        make_layout_label=True,
        make_connectors=True,
        make_sub_elements=True,
        add_elements_to_super_elements=False,
        add_mapping_to_map=True,
        add_super_model_element_to_mapping=False,
    ):
        model_element = map_.new_model_element(model_cls)
        model_element.id = glyph.id
        layout_element = map_.new_layout_element(layout_cls)
        layout_element.id = glyph.id
        layout_element.width = glyph.bbox.w
        layout_element.height = glyph.bbox.h
        layout_element.position = momapy.geometry.PointBuilder(
            glyph.bbox.x + glyph.bbox.w / 2, glyph.bbox.y + glyph.bbox.h / 2
        )
        if glyph.label is not None and glyph.label.text is not None:
            if make_model_label:
                model_element.label = glyph.label.text
            if make_layout_label:
                text_layout = momapy.core.TextLayoutBuilder()
                text_layout.position = layout_element.position
                text_layout.text = glyph.label.text
                text_layout.font_family = cls._DEFAULT_FONT_FAMILY
                text_layout.font_size = cls._DEFAULT_FONT_SIZE
                text_layout.font_color = cls._DEFAULT_FONT_COLOR
                layout_element.label = text_layout
        if make_connectors:
            for port in glyph.port:
                if port.x < glyph.bbox.x:  # LEFT
                    layout_element.left_connector_length = glyph.bbox.x - port.x
                    layout_element.direction = momapy.core.Direction.HORIZONTAL
                elif port.y < glyph.bbox.y:  # UP
                    layout_element.left_connector_length = glyph.bbox.y - port.y
                    layout_element.direction = momapy.core.Direction.VERTICAL
                elif port.x >= glyph.bbox.x + glyph.bbox.w:  # RIGHT
                    layout_element.right_connector_length = (
                        port.x - glyph.bbox.x - glyph.bbox.w
                    )
                    layout_element.direction = momapy.core.Direction.HORIZONTAL
                elif port.y >= glyph.bbox.y + glyph.bbox.h:  # DOWN
                    layout_element.right_connector_length = (
                        port.y - glyph.bbox.y - glyph.bbox.h
                    )
                    layout_element.direction = momapy.core.Direction.VERTICAL
                d_model_element_ids[port.id] = model_element
                d_layout_element_ids[port.id] = layout_element
        if make_sub_elements:
            for sub_glyph in glyph.glyph:
                (
                    sub_model_element,
                    sub_layout_element,
                ) = cls._map_elements_from_sbgnml_element(
                    sub_glyph,
                    map_,
                    d_model_element_ids,
                    d_layout_element_ids,
                    model_element,
                    layout_element,
                )
        if add_elements_to_super_elements:
            super_model_element.add_element(model_element)
            super_layout_element.add_element(layout_element)
        if add_mapping_to_map:
            if add_super_model_element_to_mapping:
                map_.add_mapping(
                    (model_element, super_model_element), layout_element
                )
            else:
                map_.add_mapping(model_element, layout_element)
        d_model_element_ids[glyph.id] = model_element
        d_layout_element_ids[glyph.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _entity_pool_node_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        return cls._node_elements_from_glyph_and_cls(
            glyph,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_model_label=True,
            make_layout_label=True,
            make_connectors=False,
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=False,
        )

    @classmethod
    def _subunit_node_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        return cls._node_elements_from_glyph_and_cls(
            glyph,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_model_label=True,
            make_layout_label=True,
            make_connectors=False,
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=True,
        )

    @classmethod
    def _auxiliary_node_no_model_label_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        return cls._node_elements_from_glyph_and_cls(
            glyph,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_model_label=False,
            make_connectors=False,
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=True,
        )

    @classmethod
    def _process_node_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        return cls._node_elements_from_glyph_and_cls(
            glyph,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_model_label=False,
            make_connectors=True,
            make_sub_elements=False,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=False,
        )

    @classmethod
    def _operator_node_elements_from_glyph_and_cls(
        cls,
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        return cls._node_elements_from_glyph_and_cls(
            glyph,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_model_label=False,
            make_connectors=True,
            make_sub_elements=False,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=False,
        )

    @classmethod
    def _arc_elements_from_arc_and_cls(
        cls,
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
        make_sub_elements=True,
        add_elements_to_super_elements=False,
        add_mapping_to_map=True,
        add_super_model_element_to_mapping=False,
        reverse_points_order=False,
    ):
        model_element = map_.new_model_element(model_cls)
        model_element.id = arc.id
        layout_element = map_.new_layout_element(layout_cls)
        layout_element.id = arc.id
        if reverse_points_order:
            sbgnml_points = [arc.end] + arc.next[::-1] + [arc.start]
        else:
            sbgnml_points = [arc.start] + arc.next + [arc.end]
        for i, sbgnml_current_point in enumerate(sbgnml_points[1:]):
            sbgnml_previous_point = sbgnml_points[i]
            current_point = momapy.geometry.PointBuilder(
                sbgnml_current_point.x, sbgnml_current_point.y
            )
            previous_point = momapy.geometry.PointBuilder(
                sbgnml_previous_point.x, sbgnml_previous_point.y
            )
            segment = momapy.builder.get_or_make_builder_cls(
                momapy.geometry.Segment
            )(previous_point, current_point)
            layout_element.segments.append(segment)
        if make_sub_elements:
            for sub_glyph in arc.glyph:
                (
                    sub_model_element,
                    sub_layout_element,
                ) = cls._map_elements_from_sbgnml_element(
                    sub_glyph,
                    map_,
                    d_model_element_ids,
                    d_layout_element_ids,
                    model_element,
                    layout_element,
                )
        if add_elements_to_super_elements:
            super_model_element.add_element(model_element)
            super_layout_element.add_element(layout_element)
        if add_mapping_to_map:
            if add_super_model_element_to_mapping:
                map_.add_mapping(
                    (model_element, super_model_element), layout_element
                )
            else:
                map_.add_mapping(model_element, layout_element)
        d_model_element_ids[arc.id] = model_element
        d_layout_element_ids[arc.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _flux_arc_elements_from_arc_and_cls(
        cls,
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
        reverse_points_order=False,
    ):
        model_element, layout_element = cls._arc_elements_from_arc_and_cls(
            arc,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=True,
            reverse_points_order=reverse_points_order,
        )
        return model_element, layout_element

    @classmethod
    def _modulation_arc_elements_from_arc_and_cls(
        cls,
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        model_element, layout_element = cls._arc_elements_from_arc_and_cls(
            arc,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=False,
        )
        model_element.source = d_model_element_ids[arc.source]
        model_element.target = d_model_element_ids[arc.target]
        layout_element.source = d_layout_element_ids[arc.source]
        layout_element.target = d_layout_element_ids[arc.target]
        return model_element, layout_element

    @classmethod
    def _compartment_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).Compartment,
            cls._get_module_from_map(map_).CompartmentLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _submap_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).Submap,
            cls._get_module_from_map(map_).SubmapLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _biological_activity_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.BiologicalActivity,
            momapy.sbgn.af.BiologicalActivityLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unspecified_entity_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.UnspecifiedEntity,
            momapy.sbgn.pd.UnspecifiedEntityLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _macromolecule_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.Macromolecule,
            momapy.sbgn.pd.MacromoleculeLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _macromolecule_multimer_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.MacromoleculeMultimer,
            momapy.sbgn.pd.MacromoleculeMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _simple_chemical_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.SimpleChemical,
            momapy.sbgn.pd.SimpleChemicalLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _simple_chemical_multimer_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.SimpleChemicalMultimer,
            momapy.sbgn.pd.SimpleChemicalMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _nucleic_acid_feature_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.NucleicAcidFeature,
            momapy.sbgn.pd.NucleicAcidFeatureLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _nucleic_acid_feature_multimer_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.NucleicAcidFeatureMultimer,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _complex_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.Complex,
            momapy.sbgn.pd.ComplexLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _complex_multimer_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.ComplexMultimer,
            momapy.sbgn.pd.ComplexMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _empty_set_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.EmptySet,
            momapy.sbgn.pd.EmptySetLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _perturbing_agent_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.PerturbingAgent,
            momapy.sbgn.pd.PerturbingAgentLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _generic_process_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._process_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.GenericProcess,
            momapy.sbgn.pd.GenericProcessLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _association_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._process_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.Association,
            momapy.sbgn.pd.AssociationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _dissociation_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._process_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.Dissociation,
            momapy.sbgn.pd.DissociationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _uncertain_process_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._process_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.UncertainProcess,
            momapy.sbgn.pd.UncertainProcessLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _omitted_process_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._process_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.OmittedProcess,
            momapy.sbgn.pd.OmittedProcessLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _phenotype_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).Phenotype,
            cls._get_module_from_map(map_).PhenotypeLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _and_operator_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._operator_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).AndOperator,
            cls._get_module_from_map(map_).AndOperatorLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _or_operator_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._operator_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).OrOperator,
            cls._get_module_from_map(map_).OrOperatorLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _not_operator_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._operator_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).NotOperator,
            cls._get_module_from_map(map_).NotOperatorLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _delay_operator_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._operator_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).DelayOperator,
            cls._get_module_from_map(map_).DelayOperatorLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _state_variable_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._auxiliary_node_no_model_label_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.StateVariable,
            momapy.sbgn.pd.StateVariableLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        if glyph.state.value is not None:
            text = glyph.state.value
            model_element.value = glyph.state.value
        else:
            text = ""
        if glyph.state.variable is not None and glyph.state.variable != "":
            text += f"@{glyph.state.variable}"
            model_element.variable = glyph.state.variable
        else:
            variable = momapy.sbgn.pd.UndefinedVariable(
                order=len(
                    [
                        sv
                        for sv in super_model_element.state_variables
                        if momapy.builder.isinstance_or_builder(
                            sv.variable, momapy.sbgn.pd.UndefinedVariable
                        )
                    ]
                )
            )
            model_element.variable = variable
        text_layout = momapy.core.TextLayoutBuilder()
        text_layout.position = layout_element.position
        text_layout.text = text
        text_layout.font_family = cls._DEFAULT_FONT_FAMILY
        text_layout.font_size = 8.0
        text_layout.font_color = cls._DEFAULT_FONT_COLOR
        layout_element.label = text_layout
        return model_element, layout_element

    @classmethod
    def _unit_of_information_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._auxiliary_node_no_model_label_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.UnitOfInformation,
            momapy.sbgn.pd.UnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        if glyph.label is not None and glyph.label.text is not None:
            l = glyph.label.text.split(":")
            model_element.value = l[-1]
            if len(l) > 1:
                model_element.prefix = l[0]
            layout_element.label.font_size = 8.0
        return model_element, layout_element

    @classmethod
    def _unit_of_information_unspecified_entity_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.UnspecifiedEntityUnitOfInformation,
            momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unit_of_information_macromolecule_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.MacromoleculeUnitOfInformation,
            momapy.sbgn.af.MacromoleculeUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unit_of_information_simple_chemical_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.SimpleChemicalUnitOfInformation,
            momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unit_of_information_nucleic_acid_feature_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.NucleicAcidFeatureUnitOfInformation,
            momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unit_of_information_complex_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.ComplexUnitOfInformation,
            momapy.sbgn.af.ComplexUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unit_of_information_perturbation_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.af.PerturbationUnitOfInformation,
            momapy.sbgn.af.PerturbationUnitOfInformationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _tag_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._entity_pool_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).Tag,
            cls._get_module_from_map(map_).TagLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _terminal_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            cls._get_module_from_map(map_).Terminal,
            cls._get_module_from_map(map_).TerminalLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        super_model_element.add_element(model_element)
        return model_element, layout_element

    @classmethod
    def _unspecified_entity_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.UnspecifiedEntitySubunit,
            momapy.sbgn.pd.UnspecifiedEntityLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _macromolecule_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.MacromoleculeSubunit,
            momapy.sbgn.pd.MacromoleculeLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _macromolecule_multimer_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.MacromoleculeMultimerSubunit,
            momapy.sbgn.pd.MacromoleculeMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _simple_chemical_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.SimpleChemicalSubunit,
            momapy.sbgn.pd.SimpleChemicalLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _simple_chemical_multimer_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.SimpleChemicalMultimerSubunit,
            momapy.sbgn.pd.SimpleChemicalMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _nucleic_acid_feature_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.NucleicAcidFeatureSubunit,
            momapy.sbgn.pd.NucleicAcidFeatureLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _nucleic_acid_feature_multimer_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunit,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _complex_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.ComplexSubunit,
            momapy.sbgn.pd.ComplexLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _complex_multimer_subunit_elements_from_glyph(
        cls,
        glyph,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._subunit_node_elements_from_glyph_and_cls(
            glyph,
            momapy.sbgn.pd.ComplexMultimerSubunit,
            momapy.sbgn.pd.ComplexMultimerLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _consumption_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        model_element, layout_element = cls._flux_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.pd.Reactant,
            momapy.sbgn.pd.ConsumptionLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            d_model_element_ids[arc.target],
            d_layout_element_ids[arc.target],
            reverse_points_order=True,
        )
        model_element.element = d_model_element_ids[arc.source]
        layout_element.target = d_layout_element_ids[
            arc.source
        ]  # the source becomes the target: in momapy flux arcs go from the process to the entity pool node; this way reversible consumptions can be represented with production layouts. Also, no source (the process layout) is set for the flux arc, so that we do not have a circular definition that would be problematic when building the object.
        return model_element, layout_element

    @classmethod
    def _production_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        process = d_model_element_ids[arc.source]
        start_x = arc.start.x
        start_y = arc.start.y
        if process.reversible:
            process_layout = map_.get_mapping(process, unpack=True)
            if process_layout.direction == momapy.core.Direction.HORIZONTAL:
                if start_x > process_layout.x:
                    model_element_cls = momapy.sbgn.pd.Product
                else:
                    model_element_cls = momapy.sbgn.pd.Reactant
            else:
                if start_y > process_layout.y:
                    model_element_cls = momapy.sbgn.pd.Product
                else:
                    model_element_cls = momapy.sbgn.pd.Reactant
        else:
            model_element_cls = momapy.sbgn.pd.Product
        model_element, layout_element = cls._flux_arc_elements_from_arc_and_cls(
            arc,
            model_element_cls,
            momapy.sbgn.pd.ProductionLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            d_model_element_ids[arc.source],
            d_layout_element_ids[arc.source],
        )
        model_element.element = d_model_element_ids[arc.target]
        layout_element.target = d_layout_element_ids[
            arc.target
        ]  # no source (the process layout) is set for the flux arc, so that we do not have a circular definition that would be problematic when building the object.
        return model_element, layout_element

    @classmethod
    def _modulation_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.pd.Modulation,
            momapy.sbgn.pd.ModulationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _stimulation_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.pd.Stimulation,
            momapy.sbgn.pd.StimulationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _catalysis_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.pd.Catalysis,
            momapy.sbgn.pd.CatalysisLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _necessary_stimulation_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            cls._get_module_from_map(map_).NecessaryStimulation,
            cls._get_module_from_map(map_).NecessaryStimulationLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _inhibition_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.pd.Inhibition,
            momapy.sbgn.pd.InhibitionLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _positive_influence_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.af.PositiveInfluence,
            momapy.sbgn.af.PositiveInfluenceLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _negative_influence_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.af.NegativeInfluence,
            momapy.sbgn.af.NegativeInfluenceLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _unknown_influence_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        (
            model_element,
            layout_element,
        ) = cls._modulation_arc_elements_from_arc_and_cls(
            arc,
            momapy.sbgn.af.UnknownInfluence,
            momapy.sbgn.af.UnknownInfluenceLayout,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
            super_layout_element,
        )
        return model_element, layout_element

    @classmethod
    def _logical_arc_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        if momapy.builder.isinstance_or_builder(
            d_model_element_ids[arc.target],
            (
                momapy.sbgn.pd.AndOperator,
                momapy.sbgn.pd.OrOperator,
                momapy.sbgn.pd.NotOperator,
                momapy.sbgn.af.AndOperator,
                momapy.sbgn.af.OrOperator,
                momapy.sbgn.af.NotOperator,
                momapy.sbgn.af.DelayOperator,
            ),
        ):
            model_cls = cls._get_module_from_map(map_).LogicalOperatorInput
        elif momapy.builder.isinstance_or_builder(
            d_model_element_ids[arc.target], momapy.sbgn.pd.EquivalenceOperator
        ):
            model_cls = momapy.sbgn.pd.EquivalenceOperatorInput
        layout_cls = cls._get_module_from_map(map_).LogicArcLayout
        model_element, layout_element = cls._arc_elements_from_arc_and_cls(
            arc,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            d_model_element_ids[arc.target],
            d_layout_element_ids[arc.target],
            make_sub_elements=True,
            add_elements_to_super_elements=True,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=True,
        )
        model_element.element = d_model_element_ids[arc.source]
        layout_element.target = d_layout_element_ids[
            arc.source
        ]  # the source becomes the target: in momapy logic arcs go from the operator to the input. Also, no source (the operator layout) is set for the logic arc, so that we do not have a circular definition that would be problematic when building the object.
        return model_element, layout_element

    @classmethod
    def _equivalence_arc_elements_from_arc(
        cls,
        arc,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
        super_model_element=None,
        super_layout_element=None,
    ):
        if momapy.builder.isinstance_or_builder(
            d_model_element_ids[arc.target],
            (momapy.sbgn.pd.Terminal,),
        ):
            model_cls = cls._get_module_from_map(map_).TerminalReference
        elif momapy.builder.isinstance_or_builder(
            d_model_element_ids[arc.target], cls._get_module_from_map(map_).Tag
        ):
            model_cls = cls._get_module_from_map(map_).TagReference
        layout_cls = cls._get_module_from_map(map_).EquivalenceArcLayout
        model_element, layout_element = cls._arc_elements_from_arc_and_cls(
            arc,
            model_cls,
            layout_cls,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            d_model_element_ids[arc.target],
            d_layout_element_ids[arc.target],
            make_sub_elements=True,
            add_elements_to_super_elements=False,
            add_mapping_to_map=True,
            add_super_model_element_to_mapping=True,
        )
        model_element.element = d_model_element_ids[arc.source]
        layout_element.target = d_layout_element_ids[
            arc.source
        ]  # the source becomes the target: in momapy equivalence arcs go from the refered element to the refering tag or terminal. Also, no source (the terminal or tag) is set for the equivalence arc, so that we do not have a circular definition that would be problematic when building the object.
        d_model_element_ids[arc.target].refers_to = model_element
        d_layout_element_ids[arc.target].add_element(layout_element)
        return model_element, layout_element

    @classmethod
    def check_file(cls, file_path):
        config = xsdata.formats.dataclass.parsers.config.ParserConfig(
            fail_on_unknown_properties=False
        )
        parser = xsdata.formats.dataclass.parsers.XmlParser(
            config=config, context=xsdata.formats.dataclass.context.XmlContext()
        )
        try:
            sbgn = parser.parse(file_path, momapy.sbgn.io._sbgnml_parser.Sbgn)
        except:
            return False
        return True


class SBGNMLWriter(momapy.io.MapWriter):
    _SBGN_CLASS_TO_TRANSFORMATION_FUNC_MAPPING = {
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
    _SBGN_QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE_MAPPING = {
        momapy.sbgn.core.BQBiol.ENCODES: (
            "encodes",
            momapy.sbgn.io._sbgnml_parser.Encodes,
        ),
        momapy.sbgn.core.BQBiol.HAS_PART: (
            "has_part",
            momapy.sbgn.io._sbgnml_parser.HasPart,
        ),
        momapy.sbgn.core.BQBiol.HAS_PROPERTY: (
            "has_property",
            momapy.sbgn.io._sbgnml_parser.HasProperty,
        ),
        momapy.sbgn.core.BQBiol.HAS_VERSION: (
            "has_version",
            momapy.sbgn.io._sbgnml_parser.HasVersion,
        ),
        momapy.sbgn.core.BQBiol.IS: (
            "is_value",
            momapy.sbgn.io._sbgnml_parser.Is1,
        ),
        momapy.sbgn.core.BQBiol.IS_DESCRIBED_BY: (
            "is_described_by",
            momapy.sbgn.io._sbgnml_parser.IsDescribedBy1,
        ),
        momapy.sbgn.core.BQBiol.IS_ENCODED_BY: (
            "is_encoded_by",
            momapy.sbgn.io._sbgnml_parser.IsEncodedBy,
        ),
        momapy.sbgn.core.BQBiol.IS_HOMOLOG_TO: (
            "is_homolog_to",
            momapy.sbgn.io._sbgnml_parser.IsHomologTo,
        ),
        momapy.sbgn.core.BQBiol.IS_PART_OF: (
            "is_part_of",
            momapy.sbgn.io._sbgnml_parser.IsPartOf,
        ),
        momapy.sbgn.core.BQBiol.IS_PROPERTY_OF: (
            "is_property_of",
            momapy.sbgn.io._sbgnml_parser.IsPropertyOf,
        ),
        momapy.sbgn.core.BQBiol.IS_VERSION_OF: (
            "is_version_of",
            momapy.sbgn.io._sbgnml_parser.IsVersionOf,
        ),
        momapy.sbgn.core.BQBiol.OCCURS_IN: (
            "occurs_in",
            momapy.sbgn.io._sbgnml_parser.OccursIn,
        ),
        momapy.sbgn.core.BQBiol.HAS_TAXON: (
            "has_taxon",
            momapy.sbgn.io._sbgnml_parser.HasTaxon,
        ),
        momapy.sbgn.core.BQModel.HAS_INSTANCE: (
            "has_instance",
            momapy.sbgn.io._sbgnml_parser.HasInstance,
        ),
        momapy.sbgn.core.BQModel.IS: (
            "biomodels_net_model_qualifiers_is",
            momapy.sbgn.io._sbgnml_parser.Is2,
        ),
        momapy.sbgn.core.BQModel.IS_DERIVED_FROM: (
            "is_derived_from",
            momapy.sbgn.io._sbgnml_parser.IsDerivedFrom,
        ),
        momapy.sbgn.core.BQModel.IS_DESCRIBED_BY: (
            "biomodels_net_model_qualifiers_is_described_by",
            momapy.sbgn.io._sbgnml_parser.IsDescribedBy2,
        ),
        momapy.sbgn.core.BQModel.IS_INSTANCE_OF: (
            "is_instance_of",
            momapy.sbgn.io._sbgnml_parser.IsInstanceOf,
        ),
    }

    @classmethod
    def write(cls, map_, file_path, with_render_information=True):
        sbgnml_map = cls._sbgnml_map_from_map(
            map_, with_render_information=with_render_information
        )
        config = xsdata.formats.dataclass.serializers.config.SerializerConfig(
            pretty_print=True
        )
        serializer = xsdata.formats.dataclass.serializers.XmlSerializer(
            config=config
        )
        xml = serializer.render(
            sbgnml_map,
            ns_map={
                "sbgn": "http://sbgn.org/libsbgn/0.2",
                "render": "http://www.sbml.org/sbml/level3/version1/render/version1",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "bqbiol": "http://biomodels.net/biology-qualifiers/",
                "bqmodel": "http://biomodels.net/model-qualifiers/",
            },
        )
        with open(file_path, "w") as f:
            f.write(xml)

    @classmethod
    def _sbgnml_map_from_map(cls, map_, with_render_information=True):
        if momapy.builder.isinstance_or_builder(map_, momapy.sbgn.pd.SBGNPDMap):
            sbgnml_language = (
                momapy.sbgn.io._sbgnml_parser.MapLanguage.PROCESS_DESCRIPTION
            )
        elif momapy.builder.isinstance_or_builder(
            map_, momapy.sbgn.af.SBGNAFMap
        ):
            sbgnml_language = (
                momapy.sbgn.io._sbgnml_parser.MapLanguage.ACTIVITY_FLOW
            )
        else:
            raise TypeError("this type of map is not supported")
        sbgnml_sbgn = momapy.sbgn.io._sbgnml_parser.Sbgn()
        sbgnml_map = momapy.sbgn.io._sbgnml_parser.Map()
        sbgnml_map.language = sbgnml_language
        sbgnml_sbgn.map = sbgnml_map
        dstyles = {}
        for layout_element in map_.layout.layout_elements:
            sbgnml_elements = cls._sbgnml_elements_from_layout_element(
                layout_element,
                map_,
                dstyles,
                map_.layout,
            )
            for sbgnml_element in sbgnml_elements:
                cls._add_sub_sbgnml_element_to_sbgnml_element(
                    sbgnml_element, sbgnml_map
                )
        if with_render_information:
            render_information = cls._render_information_from_styles(dstyles)
            render_information.id = str(uuid.uuid4())
            render_information.program_name = momapy.__about__.__name__
            render_information.program_version = momapy.__about__.__version__
            render_information.background_color = map_.layout.fill.to_hexa()
            extension = momapy.sbgn.io._sbgnml_parser.Map.Extension()
            extension.render_information = render_information
            sbgnml_map.extension = extension
        if len(map_.model.annotations) != 0:
            annotation_sbgnml_element = (
                cls._annotation_element_from_annotations(
                    map_.model.annotations, model_element.id
                )
            )
            if sbgnml_map.extension is None:
                extension = momapy.sbgn.io._sbgnml_parser.Map.Extension()
                sbgnml_map.extension = extension
            extension.annotation = annotation_sbgnml_element

        return sbgnml_sbgn

    @classmethod
    def _sbgnml_elements_from_layout_element(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        transformation_func = cls._get_transformation_func_from_layout_element(
            layout_element
        )
        if transformation_func is not None:
            sbgnml_elements = transformation_func(
                layout_element, map_, dstyles, super_layout_element
            )
            model_element = map_.get_mapping(layout_element, unpack=True)[0]
            if len(model_element.annotations) != 0:
                annotation_sbgnml_element = (
                    cls._annotation_element_from_annotations(
                        model_element.annotations, layout_element.id
                    )
                )
                extension = momapy.sbgn.io._sbgnml_parser.Map.Extension()
                extension.annotation = annotation_sbgnml_element
                sbgnml_elements[0].extension = extension
        else:
            print(
                f"object {layout_element.id}: unknown class value '{type(layout_element)}' for transformation"
            )
            sbgnml_elements = []
        return sbgnml_elements

    @classmethod
    def _add_sub_sbgnml_element_to_sbgnml_element(
        cls, sub_sbgnml_element, sbgnml_element
    ):
        if isinstance(sub_sbgnml_element, momapy.sbgn.io._sbgnml_parser.Glyph):
            sbgnml_element.glyph.append(sub_sbgnml_element)
        elif isinstance(sub_sbgnml_element, momapy.sbgn.io._sbgnml_parser.Arc):
            sbgnml_element.arc.append(sub_sbgnml_element)
        elif isinstance(
            sub_sbgnml_element, momapy.sbgn.io._sbgnml_parser.Arcgroup
        ):
            sbgnml_element.arcgroup.append(sub_sbgnml_element)

    @classmethod
    def _get_transformation_func_from_layout_element(cls, layout_element):
        if momapy.builder.isinstance_or_builder(
            layout_element, momapy.builder.Builder
        ):
            layout_element_cls = type(layout_element)._cls_to_build
        else:
            layout_element_cls = type(layout_element)
        transformation_func_name = (
            cls._SBGN_CLASS_TO_TRANSFORMATION_FUNC_MAPPING.get(
                layout_element_cls
            )
        )
        if transformation_func_name is not None:
            return getattr(cls, transformation_func_name)
        else:
            return None

    @classmethod
    def _render_information_from_styles(cls, dstyles):
        dcolors = {}
        render_information = momapy.sbgn.io._sbgnml_parser.RenderInformation()
        list_of_styles = momapy.sbgn.io._sbgnml_parser.ListOfStylesType()
        render_information.list_of_styles = list_of_styles
        list_of_color_definitions = (
            momapy.sbgn.io._sbgnml_parser.ListOfColorDefinitionsType()
        )
        render_information.list_of_color_definitions = list_of_color_definitions
        for style in dstyles:
            for attr in ["stroke", "fill"]:
                if attr in style:
                    color = style[attr]
                    if (
                        color is not None
                        and color is not momapy.drawing.NoneValue
                    ):
                        if color.to_hexa() not in dcolors:
                            dcolors[color.to_hexa()] = str(uuid.uuid4())
            sbgnml_style = momapy.sbgn.io._sbgnml_parser.StyleType()
            sbgnml_style.id = str(uuid.uuid4())
            sbgnml_style.id_list = " ".join(dstyles[style])
            sbgnml_g = momapy.sbgn.io._sbgnml_parser.GType()
            for attr in ["stroke", "fill"]:
                if (
                    attr in style
                    and style[attr] is not None
                    and style[attr] is not momapy.drawing.NoneValue
                ):
                    setattr(sbgnml_g, attr, dcolors[style[attr].to_hexa()])
            for attr in [
                "stroke_width",
                "font_family",
                "font_size",
                "font_color",
            ]:
                if attr in style:
                    setattr(sbgnml_g, attr, style[attr])
            sbgnml_style.g = sbgnml_g
            render_information.list_of_styles.style.append(sbgnml_style)
        for color in dcolors:
            color_definition = (
                momapy.sbgn.io._sbgnml_parser.ColorDefinitionType()
            )
            color_definition.id = dcolors[color]
            color_definition.value = color
            render_information.list_of_color_definitions.color_definition.append(
                color_definition
            )
        return render_information

    @classmethod
    def _annotation_element_from_annotations(cls, annotations, element_id):
        annotation_element = momapy.sbgn.io._sbgnml_parser.Annotation()
        rdf = momapy.sbgn.io._sbgnml_parser.Rdf()
        annotation_element.rdf = rdf
        description = momapy.sbgn.io._sbgnml_parser.DescriptionType()
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
                qualifier_cls,
            ) = cls._SBGN_QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE_MAPPING[
                qualifier_member
            ]
            qualifier_element = qualifier_cls()
            bag = momapy.sbgn.io._sbgnml_parser.Bag()
            qualifier_element.bag = bag
            for resource in resources:
                li = momapy.sbgn.io._sbgnml_parser.LiType()
                li.resource = resource
                bag.li.append(li)
            setattr(description, qualifier_attribute, qualifier_element)
        return annotation_element

    @classmethod
    def _node_layout_to_sbgnml_elements(
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
        sbgnml_elements = []
        glyph = momapy.sbgn.io._sbgnml_parser.Glyph()
        glyph.id = layout_element.id
        glyph.class_value = class_value
        bbox = momapy.sbgn.io._sbgnml_parser.Bbox()
        bbox.x = layout_element.x - layout_element.width / 2
        bbox.y = layout_element.y - layout_element.height / 2
        bbox.w = layout_element.width
        bbox.h = layout_element.height
        glyph.bbox = bbox
        if make_label and layout_element.label is not None:
            sbgnml_label = momapy.sbgn.io._sbgnml_parser.Label()
            sbgnml_label.text = layout_element.label.text
            glyph.label = sbgnml_label
            ink_bbox = layout_element.label.ink_bbox()
            label_bbox = momapy.sbgn.io._sbgnml_parser.Bbox()
            label_bbox.x = ink_bbox.x - ink_bbox.width / 2
            label_bbox.y = ink_bbox.y - ink_bbox.height / 2
            label_bbox.w = ink_bbox.width
            label_bbox.h = ink_bbox.height
            sbgnml_label.bbox = label_bbox
        sbgnml_elements.append(glyph)
        if make_sub_elements:
            for sub_layout_element in layout_element.layout_elements:
                sub_sbgnml_elements = cls._sbgnml_elements_from_layout_element(
                    sub_layout_element,
                    map_,
                    dstyles,
                    layout_element,
                )
                if add_sub_elements_to_element:
                    for sub_sbgnml_element in sub_sbgnml_elements:
                        cls._add_sub_sbgnml_element_to_sbgnml_element(
                            sub_sbgnml_element, glyph
                        )
                if add_sub_elements_to_return:
                    sbgnml_elements += sub_sbgnml_elements
        lattrs = [
            ("stroke", layout_element.stroke),
            ("fill", layout_element.fill),
            ("stroke_width", layout_element.stroke_width),
        ]
        if layout_element.label is not None:
            lattrs += [
                ("font_family", layout_element.label.font_family),
                ("font_size", layout_element.label.font_size),
                ("font_color", layout_element.label.font_color.to_hex()),
            ]
        style = frozendict.frozendict(lattrs)
        if style not in dstyles:
            dstyles[style] = [glyph.id]
        else:
            dstyles[style].append(glyph.id)
        return sbgnml_elements

    @classmethod
    def _entity_node_layout_to_sbgnml_elements(
        cls, layout_element, class_value, map_, dstyles
    ):
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgnml_elements

    @classmethod
    def _compartment_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.COMPARTMENT
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element, class_value, map_, dstyles
        )
        return sbgnml_elements

    @classmethod
    def _submap_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.SUBMAP
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _unspecified_entity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNSPECIFIED_ENTITY
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _macromolecule_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.MACROMOLECULE
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _simple_chemical_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.SIMPLE_CHEMICAL
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _nucleic_acid_feature_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.NUCLEIC_ACID_FEATURE
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _complex_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.COMPLEX
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _macromolecule_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.MACROMOLECULE_MULTIMER
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _simple_chemical_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.SIMPLE_CHEMICAL_MULTIMER
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _nucleic_acid_feature_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.NUCLEIC_ACID_FEATURE_MULTIMER
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _complex_multimer_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.COMPLEX_MULTIMER
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _perturbing_agent_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.PERTURBING_AGENT
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _empty_set_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.SOURCE_AND_SINK
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _biological_activity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.BIOLOGICAL_ACTIVITY
        )
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _auxiliary_unit_layout_to_sbgnml_elements(
        cls, layout_element, class_value, map_, dstyles, super_layout_element
    ):
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=False,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgnml_elements

    @classmethod
    def _state_variable_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.STATE_VARIABLE
        sbgnml_elements = cls._auxiliary_unit_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            super_layout_element,
        )
        glyph = sbgnml_elements[0]
        state_variable = map_.get_mapping(layout_element, unpack=True)[0]
        sbgnml_state = momapy.sbgn.io._sbgnml_parser.Glyph.State()
        sbgnml_state.value = state_variable.value
        sbgnml_state.variable = (
            state_variable.variable
            if not momapy.builder.isinstance_or_builder(
                state_variable.variable, momapy.sbgn.pd.UndefinedVariable
            )
            else None
        )
        glyph.state = sbgnml_state
        return sbgnml_elements

    @classmethod
    def _unit_of_information_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_unspecified_entity_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.UNSPECIFIED_ENTITY
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_macromolecule_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.MACROMOLECULE
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_simple_chemical_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.SIMPLE_CHEMICAL
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_nucleic_acid_feature_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.NUCLEIC_ACID_FEATURE
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_complex_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.COMPLEX
        )
        return sbgnml_elements

    @classmethod
    def _unit_of_information_perturbation_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.GlyphClass.UNIT_OF_INFORMATION
        )
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=True,
            add_sub_elements_to_return=False,
        )
        glyph = sbgnml_elements[0]
        glyph.entity = momapy.sbgn.io._sbgnml_parser.Glyph.Entity(
            name=momapy.sbgn.io._sbgnml_parser.EntityName.PERTURBATION
        )
        return sbgnml_elements

    @classmethod
    def _terminal_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.TERMINAL
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        return sbgnml_elements

    @classmethod
    def _tag_to_glyph(cls, layout_element, map_, dstyles, super_layout_element):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.TAG
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        return sbgnml_elements

    @classmethod
    def _process_node_layout_to_sbgnml_elements(
        cls,
        layout_element,
        class_value,
        map_,
        dstyles,
    ):
        sbgnml_elements = cls._node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
            make_label=True,
            make_sub_elements=True,
            add_sub_elements_to_element=False,
            add_sub_elements_to_return=True,
        )
        glyph = sbgnml_elements[0]
        if layout_element.direction == momapy.core.Direction.HORIZONTAL:
            glyph.orientation = (
                momapy.sbgn.io._sbgnml_parser.GlyphOrientation.HORIZONTAL
            )
        else:
            glyph.orientation = (
                momapy.sbgn.io._sbgnml_parser.GlyphOrientation.VERTICAL
            )
        left_port = momapy.sbgn.io._sbgnml_parser.Port()
        left_port.id = f"{layout_element.id}_left_port"
        left_connector_tip = layout_element.left_connector_tip()
        left_port.x = left_connector_tip.x
        left_port.y = left_connector_tip.y
        glyph.port.append(left_port)
        right_port = momapy.sbgn.io._sbgnml_parser.Port()
        right_port.id = f"{layout_element.id}_right_port"
        right_connector_tip = layout_element.right_connector_tip()
        right_port.x = right_connector_tip.x
        right_port.y = right_connector_tip.y
        glyph.port.append(right_port)
        return sbgnml_elements

    @classmethod
    def _generic_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.PROCESS
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _uncertain_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.UNCERTAIN_PROCESS
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _omitted_process_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.OMITTED_PROCESS
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _association_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.ASSOCIATION
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _dissociation_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.DISSOCIATION
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _phenotype_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.PHENOTYPE
        sbgnml_elements = cls._entity_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )

        return sbgnml_elements

    @classmethod
    def _and_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.AND
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _or_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.OR
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _not_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.NOT
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _equivalence_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.EQUIVALENCE
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _delay_operator_to_glyph(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.GlyphClass.DELAY
        sbgnml_elements = cls._process_node_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            map_,
            dstyles,
        )
        return sbgnml_elements

    @classmethod
    def _arc_layout_to_sbgnml_elements(
        cls,
        layout_element,
        class_value,
        source_id,
        target_id,
        dstyles,
        reverse_points_order=False,
    ):
        sbgnml_elements = []
        arc = momapy.sbgn.io._sbgnml_parser.Arc()
        arc.class_value = class_value
        arc.id = layout_element.id
        points = layout_element.points()
        if reverse_points_order:
            start_point = points[-1]
            end_point = points[0]
        else:
            start_point = points[0]
            end_point = points[-1]
        start = momapy.sbgn.io._sbgnml_parser.Arc.Start()
        start.x = start_point.x
        start.y = start_point.y
        arc.start = start
        end = momapy.sbgn.io._sbgnml_parser.Arc.End()
        end.x = end_point.x
        end.y = end_point.y
        arc.end = end
        arc.source = source_id
        arc.target = target_id
        sbgnml_elements.append(arc)
        for sub_layout_element in layout_element.layout_elements:
            sub_sbgnml_elements = cls._sbgnml_elements_from_layout_element(
                sub_layout_element,
                map_,
                layout_element,
            )
            for sub_sbgnml_element in sub_sbgnml_elements:
                cls._add_sub_sbgnml_element_to_sbgnml_element(
                    sub_sbgnml_element, arc
                )
        style = frozendict.frozendict(
            [
                ("stroke", layout_element.stroke),
                ("fill", layout_element.fill),
                ("stroke_width", layout_element.stroke_width),
            ]
        )
        if style not in dstyles:
            dstyles[style] = [arc.id]
        else:
            dstyles[style].append(arc.id)
        return sbgnml_elements

    @classmethod
    def _consumption_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.CONSUMPTION
        source_id = layout_element.target.id
        if super_layout_element.left_to_right:
            target_id = f"{super_layout_element.id}_left_port"
        else:
            target_id = f"{super_layout_element.id}_right_port"
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgnml_elements

    @classmethod
    def _production_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.PRODUCTION
        target_id = layout_element.target.id
        if super_layout_element.left_to_right:
            source_id = f"{super_layout_element.id}_right_port"
        else:
            source_id = f"{super_layout_element.id}_left_port"
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _modulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.MODULATION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _stimulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.STIMULATION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _necessary_stimulation_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = (
            momapy.sbgn.io._sbgnml_parser.ArcClass.NECESSARY_STIMULATION
        )
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _catalysis_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.CATALYSIS
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _inhibition_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.INHIBITION
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _unknown_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.UNKNOWN_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _positive_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.POSITIVE_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _negative_influence_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.NEGATIVE_INFLUENCE
        source_id = layout_element.source.id
        target_id = layout_element.target.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=False,
        )
        return sbgnml_elements

    @classmethod
    def _logic_arc_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.LOGIC_ARC
        source_id = layout_element.target.id
        if super_layout_element.left_to_right:
            target_id = f"{super_layout_element.id}_left_port"
        else:
            target_id = f"{super_layout_element.id}_right_port"
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgnml_elements

    @classmethod
    def _equivalence_arc_to_arc(
        cls, layout_element, map_, dstyles, super_layout_element
    ):
        class_value = momapy.sbgn.io._sbgnml_parser.ArcClass.EQUIVALENCE_ARC
        source_id = layout_element.target.id
        target_id = super_layout_element.id
        sbgnml_elements = cls._arc_layout_to_sbgnml_elements(
            layout_element,
            class_value,
            source_id,
            target_id,
            dstyles,
            reverse_points_order=True,
        )
        return sbgnml_elements


momapy.io.register_reader("sbgnml", SBGNMLReader)
momapy.io.register_writer("sbgnml", SBGNMLWriter)
