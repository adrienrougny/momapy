import xsdata.formats.dataclass.context
import xsdata.formats.dataclass.parsers
import xsdata.formats.dataclass.parsers.config

import momapy.core
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.styling
import momapy.rendering.core
import momapy.rendering.skia
import momapy.sbgn.parser
import momapy.sbgn.pd
import momapy.sbgn.af

_DEFAULT_FONT_FAMILY = "Helvetica"
_DEFAULT_FONT_SIZE = 14.0
_DEFAULT_FONT_COLOR = momapy.coloring.black


def read_file(file_path, return_builder=False):
    config = xsdata.formats.dataclass.parsers.config.ParserConfig(
        fail_on_unknown_properties=False
    )
    parser = xsdata.formats.dataclass.parsers.XmlParser(
        config=config, context=xsdata.formats.dataclass.context.XmlContext()
    )
    sbgn = parser.parse(file_path, momapy.sbgn.parser.Sbgn)
    sbgn_map = sbgn.map
    map_ = _map_from_sbgn_map(sbgn_map)
    if sbgn_map.extension.render_information is not None:
        style_sheet = _style_sheet_from_render_information(
            sbgn_map.extension.render_information
        )
        momapy.styling.apply_style_sheet(map_.layout, style_sheet)
    if not return_builder:
        map_ = momapy.builder.object_from_builder(map_)
    return map_


def _get_module_from_map(map_):
    if momapy.builder.isinstance_or_builder(map_, momapy.sbgn.pd.SBGNPDMap):
        return momapy.sbgn.pd
    else:
        return momapy.sbgn.af


def _map_from_sbgn_map(sbgn_map):
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
        model_element, layout_element = _map_elements_from_sbgnml_element(
            glyph, map_, d_model_element_ids, d_layout_element_ids
        )
    for arc in sbgn_map.arc:
        model_element, layout_element = _map_elements_from_sbgnml_element(
            arc, map_, d_model_element_ids, d_layout_element_ids
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


def _style_sheet_from_render_information(render_information):
    style_sheet = momapy.styling.StyleSheet()
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
                label_style_collection[attr] = momapy.coloring.Color.from_hex(
                    color_str
                )
        style_sheet[label_selector] = label_style_collection
    return style_sheet


def _get_transformation_func_from_class_value(
    class_value, super_model_element=None
):
    class_str = class_value.name
    if super_model_element is not None:
        if class_str in [
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
        elif class_str == "TAG":
            if momapy.builder.isinstance_or_builder(
                super_model_element,
                (momapy.sbgn.pd.Submap, momapy.sbgn.af.Submap),
            ):
                class_str = "TERMINAL"
    return SBGNML_ELEMENT_CLASS_TO_TRANSFORMATION_FUNC_MAPPING.get(class_str)


def _map_elements_from_sbgnml_element(
    sbgn_element,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    transformation_func = _get_transformation_func_from_class_value(
        sbgn_element.class_value, super_model_element
    )
    if transformation_func is not None:
        model_element, layout_element = transformation_func(
            sbgn_element,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            super_model_element,
        )
    else:
        print(
            f"object {sbgn_element.id}: unknown class value '{sbgn_element.class_value}' for transformation"
        )
        model_element = None
        layout_element = None
    return model_element, layout_element


def _node_elements_from_glyph_and_cls(
    glyph,
    model_cls,
    layout_cls,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
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
        model_element.label = glyph.label.text
        text_layout = momapy.core.TextLayoutBuilder()
        text_layout.position = layout_element.position
        text_layout.text = glyph.label.text
        text_layout.font_family = _DEFAULT_FONT_FAMILY
        text_layout.font_size = _DEFAULT_FONT_SIZE
        text_layout.font_color = _DEFAULT_FONT_COLOR
        layout_element.label = text_layout
    d_model_element_ids[glyph.id] = model_element
    d_layout_element_ids[glyph.id] = layout_element
    return model_element, layout_element


def _node_with_subnodes_elements_from_glyph_and_cls(
    glyph,
    model_cls,
    layout_cls,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
):
    model_element, layout_element = _node_elements_from_glyph_and_cls(
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    map_.add_model_element(model_element)
    map_.add_layout_element(layout_element)
    map_.add_mapping(model_element, layout_element)
    for sub_glyph in glyph.glyph:
        (
            sub_model_element,
            sub_layout_element,
        ) = _map_elements_from_sbgnml_element(
            sub_glyph,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            model_element,
        )
        if sub_model_element is not None:
            model_element.add_element(sub_model_element)
            layout_element.add_element(sub_layout_element)
            map_.add_mapping((sub_model_element, model_element), layout_element)
    return model_element, layout_element


def _subunit_elements_from_glyph_and_cls(
    glyph,
    model_cls,
    layout_cls,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
):
    model_element, layout_element = _node_elements_from_glyph_and_cls(
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    for sub_glyph in glyph.glyph:
        (
            sub_model_element,
            sub_layout_element,
        ) = _map_elements_from_sbgnml_element(
            sub_glyph,
            map_,
            d_model_element_ids,
            d_layout_element_ids,
            model_element,
        )
        if sub_model_element is not None:
            model_element.add_element(sub_model_element)
            layout_element.add_element(sub_layout_element)
            map_.add_mapping((sub_model_element, model_element), layout_element)
    return model_element, layout_element


def _node_with_connectors_elements_from_glyph_and_cls(
    glyph,
    model_cls,
    layout_cls,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
):
    model_element, layout_element = _node_elements_from_glyph_and_cls(
        glyph,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
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
    map_.add_model_element(model_element)
    map_.add_layout_element(layout_element)
    map_.add_mapping(model_element, layout_element)
    return model_element, layout_element


def _arc_elements_from_arc_and_cls(
    arc, model_cls, layout_cls, map_, d_model_element_ids, d_layout_element_ids
):
    model_element = map_.new_model_element(model_cls)
    model_element.id = arc.id
    layout_element = map_.new_layout_element(layout_cls)
    layout_element.id = arc.id
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
    d_model_element_ids[arc.id] = model_element
    d_layout_element_ids[arc.id] = layout_element
    return model_element, layout_element


def _flux_elements_from_arc_and_cls(
    arc, model_cls, layout_cls, map_, d_model_element_ids, d_layout_element_ids
):
    model_element, layout_element = _arc_elements_from_arc_and_cls(
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _modulation_arc_elements_from_arc_and_cls(
    arc, model_cls, layout_cls, map_, d_model_element_ids, d_layout_element_ids
):
    model_element, layout_element = _arc_elements_from_arc_and_cls(
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.source = d_model_element_ids[arc.source]
    model_element.target = d_model_element_ids[arc.target]
    layout_element.source = d_layout_element_ids[arc.source]
    layout_element.target = d_layout_element_ids[arc.target]
    map_.add_model_element(model_element)
    map_.add_layout_element(layout_element)
    return model_element, layout_element


def _compartment_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _node_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).Compartment,
        _get_module_from_map(map_).CompartmentLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    map_.add_model_element(model_element)
    map_.add_layout_element(layout_element)
    map_.add_mapping(model_element, layout_element)
    return model_element, layout_element


def _submap_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).Submap,
        _get_module_from_map(map_).SubmapLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _biological_activity_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.af.BiologicalActivity,
        momapy.sbgn.af.BiologicalActivityLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _unspecified_entity_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.UnspecifiedEntity,
        momapy.sbgn.pd.UnspecifiedEntityLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _macromolecule_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.Macromolecule,
        momapy.sbgn.pd.MacromoleculeLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _macromolecule_multimer_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.MacromoleculeMultimer,
        momapy.sbgn.pd.MacromoleculeMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _simple_chemical_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.SimpleChemical,
        momapy.sbgn.pd.SimpleChemicalLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _simple_chemical_multimer_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.SimpleChemicalMultimer,
        momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _nucleic_acid_feature_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.NucleicAcidFeature,
        momapy.sbgn.pd.NucleicAcidFeatureLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _nucleic_acid_feature_multimer_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.NucleicAcidFeatureMultimer,
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _complex_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.Complex,
        momapy.sbgn.pd.ComplexLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _complex_multimer_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.ComplexMultimer,
        momapy.sbgn.pd.ComplexMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _empty_set_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.EmptySet,
        momapy.sbgn.pd.EmptySetLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _perturbing_agent_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.PerturbingAgent,
        momapy.sbgn.pd.PerturbingAgentLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _generic_process_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.GenericProcess,
        momapy.sbgn.pd.GenericProcessLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _association_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.Association,
        momapy.sbgn.pd.AssociationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _dissociation_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.Dissociation,
        momapy.sbgn.pd.DissociationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _uncertain_process_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.UncertainProcess,
        momapy.sbgn.pd.UncertainProcessLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _omitted_process_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.OmittedProcess,
        momapy.sbgn.pd.OmittedProcessLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _phenotype_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).Phenotype,
        _get_module_from_map(map_).PhenotypeLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    map_.add_model_element(model_element)
    map_.add_layout_element(layout_element)
    map_.add_mapping(model_element, layout_element)
    return model_element, layout_element


def _and_operator_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).AndOperator,
        _get_module_from_map(map_).AndOperatorLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _or_operator_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).OrOperator,
        _get_module_from_map(map_).OrOperatorLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _not_operator_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).NotOperator,
        _get_module_from_map(map_).NotOperatorLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _delay_operator_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_connectors_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).DelayOperator,
        _get_module_from_map(map_).DelayOperatorLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _state_variable_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element,
):
    (
        model_element,
        layout_element,
    ) = _node_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.StateVariable,
        momapy.sbgn.pd.StateVariableLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
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
    text_layout.font_family = _DEFAULT_FONT_FAMILY
    text_layout.font_size = 8.0
    text_layout.font_color = _DEFAULT_FONT_COLOR
    layout_element.label = text_layout
    return model_element, layout_element


def _unit_of_information_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element,
):
    (
        model_element,
        layout_element,
    ) = _node_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.UnitOfInformation,
        momapy.sbgn.pd.UnitOfInformationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    if glyph.label is not None and glyph.label.text is not None:
        l = glyph.label.text.split(":")
        model_element.value = l[-1]
        if len(l) > 1:
            model_element.prefix = l[0]
        layout_element.label.font_size = 8.0
    return model_element, layout_element


def _tag_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_with_subnodes_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).Tag,
        _get_module_from_map(map_).TagLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _terminal_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _node_elements_from_glyph_and_cls(
        glyph,
        _get_module_from_map(map_).Terminal,
        _get_module_from_map(map_).TerminalLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    super_model_element.add_element(model_element)
    return model_element, layout_element


def _unspecified_entity_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.UnspecifiedEntitySubunit,
        momapy.sbgn.pd.UnspecifiedEntityLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _macromolecule_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.MacromoleculeSubunit,
        momapy.sbgn.pd.MacromoleculeLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _macromolecule_multimer_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.MacromoleculeMultimerSubunit,
        momapy.sbgn.pd.MacromoleculeMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _simple_chemical_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.SimpleChemicalSubunit,
        momapy.sbgn.pd.SimpleChemicalLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _simple_chemical_multimer_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.SimpleChemicalMultimerSubunit,
        momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _nucleic_acid_feature_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.NucleicAcidFeatureSubunit,
        momapy.sbgn.pd.NucleicAcidFeatureLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _nucleic_acid_feature_multimer_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunit,
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _complex_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.ComplexSubunit,
        momapy.sbgn.pd.ComplexLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _complex_multimer_subunit_elements_from_glyph(
    glyph,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    (
        model_element,
        layout_element,
    ) = _subunit_elements_from_glyph_and_cls(
        glyph,
        momapy.sbgn.pd.ComplexMultimerSubunit,
        momapy.sbgn.pd.ComplexMultimerLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _consumption_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _flux_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Reactant,
        momapy.sbgn.pd.ConsumptionLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.element = d_model_element_ids[arc.source]
    layout_element.target = d_layout_element_ids[
        arc.source
    ]  # the source becomes the target: in momapy flux arcs go from the process to the entity pool node; this way reversible consumptions can be represented with production layouts. Also, no source (the process layout) is set for the flux arc, so that we do not have a circular definition that would be problematic when building the object.
    d_model_element_ids[arc.target].add_element(model_element)
    d_layout_element_ids[arc.target].add_element(layout_element)
    return model_element, layout_element


def _production_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _flux_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Product,
        momapy.sbgn.pd.ProductionLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.element = d_model_element_ids[arc.target]
    layout_element.target = d_layout_element_ids[
        arc.target
    ]  # no source (the process layout) is set for the flux arc, so that we do not have a circular definition that would be problematic when building the object.
    d_model_element_ids[arc.source].add_element(model_element)
    d_layout_element_ids[arc.source].add_element(layout_element)
    return model_element, layout_element


def _modulation_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Modulation,
        momapy.sbgn.pd.ModulationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _stimulation_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Stimulation,
        momapy.sbgn.pd.StimulationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _catalysis_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Catalysis,
        momapy.sbgn.pd.CatalysisLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _necessary_stimulation_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        _get_module_from_map(map_).NecessaryStimulation,
        _get_module_from_map(map_).NecessaryStimulationLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _inhibition_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.pd.Inhibition,
        momapy.sbgn.pd.InhibitionLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _positive_influence_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.af.PositiveInfluence,
        momapy.sbgn.af.PositiveInfluenceLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _negative_influence_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.af.NegativeInfluence,
        momapy.sbgn.af.NegativeInfluenceLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _unknown_influence_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    model_element, layout_element = _modulation_arc_elements_from_arc_and_cls(
        arc,
        momapy.sbgn.af.UnknownInfluence,
        momapy.sbgn.af.UnknownInfluenceLayout,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    return model_element, layout_element


def _logical_arc_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
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
        model_cls = _get_module_from_map(map_).LogicalOperatorInput
    elif momapy.builder.isinstance_or_builder(
        d_model_element_ids[arc.target], momapy.sbgn.pd.EquivalenceOperator
    ):
        model_cls = momapy.sbgn.pd.EquivalenceOperatorInput
    layout_cls = _get_module_from_map(map_).LogicArcLayout
    model_element, layout_element = _arc_elements_from_arc_and_cls(
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.element = d_model_element_ids[arc.source]
    layout_element.target = d_layout_element_ids[
        arc.source
    ]  # the source becomes the target: in momapy logic arcs go from the operator to the input. Also, no source (the operator layout) is set for the logic arc, so that we do not have a circular definition that would be problematic when building the object.
    d_model_element_ids[arc.target].add_element(model_element)
    d_layout_element_ids[arc.target].add_element(layout_element)
    return model_element, layout_element


def _equivalence_arc_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
):
    if momapy.builder.isinstance_or_builder(
        d_model_element_ids[arc.target],
        (momapy.sbgn.pd.Terminal,),
    ):
        model_cls = _get_module_from_map(map_).TerminalReference
    elif momapy.builder.isinstance_or_builder(
        d_model_element_ids[arc.target], _get_module_from_map(map_).Tag
    ):
        model_cls = _get_module_from_map(map_).TagReference
    layout_cls = _get_module_from_map(map_).EquivalenceArcLayout
    model_element, layout_element = _arc_elements_from_arc_and_cls(
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.element = d_model_element_ids[arc.source]
    layout_element.target = d_layout_element_ids[
        arc.source
    ]  # the source becomes the target: in momapy equivalence arcs go from the refered element to the refering tag or terminal. Also, no source (the terminal or tag) is set for the equivalence arc, so that we do not have a circular definition that would be problematic when building the object.
    d_model_element_ids[arc.target].refers_to = model_element
    d_layout_element_ids[arc.target].add_element(layout_element)
    return model_element, layout_element


def _logical_arc_elements_from_arc(
    arc,
    map_,
    d_model_element_ids,
    d_layout_element_ids,
    super_model_element=None,
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
        model_cls = _get_module_from_map(map_).LogicalOperatorInput
    elif momapy.builder.isinstance_or_builder(
        d_model_element_ids[arc.target], momapy.sbgn.pd.EquivalenceOperator
    ):
        model_cls = momapy.sbgn.pd.EquivalenceOperatorInput
    layout_cls = _get_module_from_map(map_).LogicArcLayout
    model_element, layout_element = _arc_elements_from_arc_and_cls(
        arc,
        model_cls,
        layout_cls,
        map_,
        d_model_element_ids,
        d_layout_element_ids,
    )
    model_element.element = d_model_element_ids[arc.source]
    layout_element.target = d_layout_element_ids[
        arc.source
    ]  # the source becomes the target: in momapy logica arcs go from the operator to the input. Also, no source (the operator layout) is set for the logic arc, so that we do not have a circular definition that would be problematic when building the object.
    d_model_element_ids[arc.target].add_element(model_element)
    d_layout_element_ids[arc.target].add_element(layout_element)
    return model_element, layout_element


SBGNML_ELEMENT_CLASS_TO_TRANSFORMATION_FUNC_MAPPING = {
    "COMPARTMENT": _compartment_elements_from_glyph,
    "SUBMAP": _submap_elements_from_glyph,
    "UNSPECIFIED_ENTITY": _unspecified_entity_elements_from_glyph,
    "MACROMOLECULE": _macromolecule_elements_from_glyph,
    "MACROMOLECULE_MULTIMER": _macromolecule_multimer_elements_from_glyph,
    "SIMPLE_CHEMICAL": _simple_chemical_elements_from_glyph,
    "SIMPLE_CHEMICAL_MULTIMER": _simple_chemical_multimer_elements_from_glyph,
    "NUCLEIC_ACID_FEATURE": _nucleic_acid_feature_elements_from_glyph,
    "NUCLEIC_ACID_FEATURE_MULTIMER": _nucleic_acid_feature_multimer_elements_from_glyph,
    "COMPLEX": _complex_elements_from_glyph,
    "COMPLEX_MULTIMER": _complex_multimer_elements_from_glyph,
    "SOURCE_AND_SINK": _empty_set_elements_from_glyph,
    "PERTURBING_AGENT": _perturbing_agent_elements_from_glyph,
    "PROCESS": _generic_process_elements_from_glyph,
    "ASSOCIATION": _association_elements_from_glyph,
    "DISSOCIATION": _dissociation_elements_from_glyph,
    "UNCERTAIN_PROCESS": _uncertain_process_elements_from_glyph,
    "OMITTED_PROCESS": _omitted_process_elements_from_glyph,
    "PHENOTYPE": _phenotype_elements_from_glyph,
    "STATE_VARIABLE": _state_variable_elements_from_glyph,
    "UNIT_OF_INFORMATION": _unit_of_information_elements_from_glyph,
    "TERMINAL": _terminal_elements_from_glyph,
    "TAG": _tag_elements_from_glyph,
    "UNSPECIFIED_ENTITY_SUBUNIT": _unspecified_entity_subunit_elements_from_glyph,
    "MACROMOLECULE_SUBUNIT": _macromolecule_subunit_elements_from_glyph,
    "MACROMOLECULE_MULTIMER_SUBUNIT": _macromolecule_multimer_subunit_elements_from_glyph,
    "SIMPLE_CHEMICAL_SUBUNIT": _simple_chemical_subunit_elements_from_glyph,
    "SIMPLE_CHEMICAL_MULTIMER_SUBUNIT": _simple_chemical_multimer_subunit_elements_from_glyph,
    "NUCLEIC_ACID_FEATURE_SUBUNIT": _nucleic_acid_feature_subunit_elements_from_glyph,
    "NUCLEIC_ACID_FEATURE_MULTIMER_SUBUNIT": _nucleic_acid_feature_multimer_subunit_elements_from_glyph,
    "COMPLEX_SUBUNIT": _complex_subunit_elements_from_glyph,
    "COMPLEX_MULTIMER_SUBUNIT": _complex_multimer_subunit_elements_from_glyph,
    "AND": _and_operator_elements_from_glyph,
    "OR": _or_operator_elements_from_glyph,
    "NOT": _not_operator_elements_from_glyph,
    "DELAY": _delay_operator_elements_from_glyph,
    "CONSUMPTION": _consumption_elements_from_arc,
    "PRODUCTION": _production_elements_from_arc,
    "MODULATION": _modulation_elements_from_arc,
    "STIMULATION": _stimulation_elements_from_arc,
    "CATALYSIS": _catalysis_elements_from_arc,
    "NECESSARY_STIMULATION": _necessary_stimulation_elements_from_arc,
    "INHIBITION": _inhibition_elements_from_arc,
    "POSITIVE_INFLUENCE": _positive_influence_elements_from_arc,
    "NEGATIVE_INFLUENCE": _negative_influence_elements_from_arc,
    "UNKNOWN_INFLUENCE": _unknown_influence_elements_from_arc,
    "LOGIC_ARC": _logical_arc_elements_from_arc,
    "EQUIVALENCE_ARC": _equivalence_arc_elements_from_arc,
}

if __name__ == "__main__":
    file_path = "test.sbgn"
    map_ = read_file(file_path)
    momapy.rendering.core.render_map(
        map_, "test.pdf", format_="pdf", renderer="skia", to_top_left=True
    )
