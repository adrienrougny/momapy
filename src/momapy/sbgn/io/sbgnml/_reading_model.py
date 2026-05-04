"""Model-building functions for SBGN-ML reader.

Each ``make_*`` function takes a ``reading_context`` as its first
argument, checks whether ``reading_context.model`` is ``None``, and
returns ``None`` early when no model is being built.
"""

import momapy.builder
import momapy.core.elements
import momapy.io.utils
import momapy.sbgn.pd
import momapy.sbgn.io.sbgnml._reading_classification
import momapy.sbgn.io.sbgnml._reading_parsing
import momapy.sbml.io.sbml._model
import momapy.sbml.io.sbml._parsing
import momapy.sbml.io.sbml._qualifiers


def make_annotations_from_element(sbgnml_element):
    sbgnml_rdf = momapy.sbgn.io.sbgnml._reading_parsing.get_rdf(sbgnml_element)
    if sbgnml_rdf is None:
        return []
    return momapy.sbml.io.sbml._model.make_annotations(sbgnml_rdf)


def make_notes_from_element(sbgnml_element):
    sbgnml_notes = momapy.sbgn.io.sbgnml._reading_parsing.get_notes(sbgnml_element)
    return momapy.sbml.io.sbml._model.make_notes(sbgnml_notes)


def make_and_add_annotations_and_notes(
    reading_context, sbgnml_element, model_element, source_id=None
):
    """Add annotations and notes from an SBGN-ML element to the context.

    Populates both the merged ``element_to_annotations`` /
    ``element_to_notes`` side tables and the per-source
    ``source_id_to_annotations`` / ``source_id_to_notes`` side tables
    when ``source_id`` is given.

    Args:
        reading_context: The reading context.
        sbgnml_element: The SBGN-ML XML element.
        model_element: The frozen model element to associate with.
        source_id: The raw source XML id of ``sbgnml_element``.  When
            ``None``, the per-source side tables are not populated
            (used for elements with no stable source id, e.g. the map
            root in SBGN-ML 0.2).
    """
    if reading_context.with_annotations:
        annotations = make_annotations_from_element(sbgnml_element)
        if annotations:
            reading_context.element_to_annotations[model_element].update(annotations)
            if source_id is not None:
                reading_context.source_id_to_annotations[source_id].update(annotations)
    if reading_context.with_notes:
        notes = make_notes_from_element(sbgnml_element)
        if notes:
            reading_context.element_to_notes[model_element].update(notes)
            if source_id is not None:
                reading_context.source_id_to_notes[source_id].update(notes)


def set_label(model_element, sbgnml_element):
    sbgnml_label = getattr(sbgnml_element, "label", None)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")


def set_compartment(model_element, sbgnml_element, sbgnml_id_to_model_element):
    sbgnml_compartment_ref = sbgnml_element.get("compartmentRef")
    if sbgnml_compartment_ref is not None:
        model_element.compartment = sbgnml_id_to_model_element[sbgnml_compartment_ref]


def set_stoichiometry(model_element, sbgnml_stoichiometry):
    if sbgnml_stoichiometry is None:
        return
    sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
    if sbgnml_label is None:
        return
    sbgnml_stoichiometry_text = sbgnml_label.get("text")
    if sbgnml_stoichiometry_text is None:
        return
    try:
        model_element.stoichiometry = float(sbgnml_stoichiometry_text)
    except ValueError:
        pass


def make_compartment(reading_context, sbgnml_compartment):
    """Create a compartment model builder.

    Args:
        reading_context: The reading context.
        sbgnml_compartment: The SBGN-ML compartment XML element.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    module = momapy.sbgn.io.sbgnml._reading_classification.get_module_from_object(
        reading_context.model
    )
    model_element = momapy.builder.new_builder_object(module.Compartment)
    model_element.id_ = f"{sbgnml_compartment.get('id')}_model"
    set_label(model_element, sbgnml_compartment)
    return model_element


def make_entity_pool_or_subunit(
    reading_context, sbgnml_entity_pool_or_subunit, model_element_cls
):
    """Create an entity pool or subunit model builder.

    Args:
        reading_context: The reading context.
        sbgnml_entity_pool_or_subunit: The SBGN-ML element.
        model_element_cls: The model element class to instantiate. May be
            None for glyphs with no model representation (e.g. empty set).

    Returns:
        A model element builder, or None if no model element should be
        created (either ``reading_context.model`` is None or
        ``model_element_cls`` is None).
    """
    if reading_context.model is None or model_element_cls is None:
        return None
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_entity_pool_or_subunit.get('id')}_model"
    set_compartment(
        model_element,
        sbgnml_entity_pool_or_subunit,
        reading_context.xml_id_to_model_element,
    )
    set_label(model_element, sbgnml_entity_pool_or_subunit)
    return model_element


def make_activity(reading_context, sbgnml_activity, model_element_cls):
    """Create an activity model builder.

    Args:
        reading_context: The reading context.
        sbgnml_activity: The SBGN-ML activity XML element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_activity.get('id')}_model"
    set_compartment(
        model_element,
        sbgnml_activity,
        reading_context.xml_id_to_model_element,
    )
    set_label(model_element, sbgnml_activity)
    return model_element


def make_state_variable(reading_context, sbgnml_state_variable, order=None):
    """Create a frozen state variable model element.

    Args:
        reading_context: The reading context.
        sbgnml_state_variable: The SBGN-ML state variable XML element.
        order: Optional ordering for undefined variables.

    Returns:
        A frozen model element, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_state_variable.get("id")
    sbgnml_state = getattr(sbgnml_state_variable, "state", None)
    if sbgnml_state is None:
        value = None
        variable = None
    else:
        sbgnml_value = sbgnml_state.get("value")
        if sbgnml_value:
            value = sbgnml_value
        else:
            value = None
        sbgnml_variable = sbgnml_state.get("variable")
        variable = sbgnml_variable
    model_element = momapy.builder.new_builder_object(momapy.sbgn.pd.StateVariable)
    model_element.id_ = f"{sbgnml_id}_model"
    model_element.value = value
    model_element.variable = variable
    model_element.order = order
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_unit_of_information(
    reading_context, sbgnml_unit_of_information, model_element_cls
):
    """Create a frozen unit of information model element.

    Args:
        reading_context: The reading context.
        sbgnml_unit_of_information: The SBGN-ML unit of information element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A frozen model element, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_label = getattr(sbgnml_unit_of_information, "label", None)
    sbgnml_id = sbgnml_unit_of_information.get("id")
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    if sbgnml_label is not None:
        split_label = sbgnml_label.get("text").split(":")
        model_element.value = split_label[-1]
        if len(split_label) > 1:
            model_element.prefix = split_label[0]
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_submap(reading_context, sbgnml_submap, model_element_cls):
    """Create a submap model builder.

    Args:
        reading_context: The reading context.
        sbgnml_submap: The SBGN-ML submap XML element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_submap.get("id")
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    set_label(model_element, sbgnml_submap)
    return model_element


def make_terminal_or_tag(reading_context, sbgnml_terminal_or_tag, is_terminal):
    """Create a terminal or tag model builder.

    Args:
        reading_context: The reading context.
        sbgnml_terminal_or_tag: The SBGN-ML terminal or tag element.
        is_terminal: True for terminal, False for tag.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_terminal_or_tag.get("id")
    if is_terminal:
        model_element_cls = momapy.sbgn.pd.Terminal
    else:
        model_element_cls = momapy.sbgn.pd.Tag
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    set_label(model_element, sbgnml_terminal_or_tag)
    return model_element


def make_reference(reading_context, sbgnml_equivalence_arc, is_terminal):
    """Create a frozen reference model element.

    Args:
        reading_context: The reading context.
        sbgnml_equivalence_arc: The SBGN-ML equivalence arc element.
        is_terminal: True for terminal reference, False for tag reference.

    Returns:
        A frozen model element, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_equivalence_arc.get("id")
    # For terminals and tags, equivalence arc goes from the referred node
    # to the terminal or tag. We invert the arc, so that the arc goes
    # from the reference to the referred node.
    sbgnml_target_id = sbgnml_equivalence_arc.get("source")
    if is_terminal:
        model_element_cls = momapy.sbgn.pd.TerminalReference
    else:
        model_element_cls = momapy.sbgn.pd.TagReference
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    target_model_element = reading_context.xml_id_to_model_element[sbgnml_target_id]
    model_element.element = target_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_stoichiometric_process(reading_context, sbgnml_process, model_element_cls):
    """Create a stoichiometric process model builder.

    Args:
        reading_context: The reading context.
        sbgnml_process: The SBGN-ML process XML element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_process.get("id")
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    model_element.reversible = (
        momapy.sbgn.io.sbgnml._reading_parsing.is_process_reversible(
            sbgnml_process, reading_context.sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    return model_element


def make_reactant(reading_context, sbgnml_consumption_arc):
    """Create a frozen reactant model element.

    Args:
        reading_context: The reading context.
        sbgnml_consumption_arc: The SBGN-ML consumption arc element.

    Returns:
        A frozen model element, or None if reading_context.model is None
        or the source glyph is an empty set (no model peer).
    """
    if reading_context.model is None:
        return None
    sbgnml_source_id = sbgnml_consumption_arc.get("source")
    if sbgnml_source_id in reading_context.empty_set_xml_ids:
        return None
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._reading_parsing.get_stoichiometry(
        sbgnml_consumption_arc
    )
    model_element = momapy.builder.new_builder_object(momapy.sbgn.pd.Reactant)
    model_element.id_ = f"{sbgnml_consumption_arc.get('id')}_model"
    source_model_element = reading_context.xml_id_to_model_element[sbgnml_source_id]
    model_element.element = source_model_element
    set_stoichiometry(model_element, sbgnml_stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_product(
    reading_context,
    sbgnml_production_arc,
    super_model_element,
    super_sbgnml_element,
    process_direction,
):
    """Create a frozen product model element.

    Args:
        reading_context: The reading context.
        sbgnml_production_arc: The SBGN-ML production arc element.
        super_model_element: The parent process model element builder.
        super_sbgnml_element: The parent process SBGN-ML element.
        process_direction: The direction of the process.

    Returns:
        A frozen model element, or None if reading_context.model is None
        or the target glyph is an empty set (no model peer).
    """
    if reading_context.model is None:
        return None
    sbgnml_target_id = sbgnml_production_arc.get("target")
    if sbgnml_target_id in reading_context.empty_set_xml_ids:
        return None
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._reading_parsing.get_stoichiometry(
        sbgnml_production_arc
    )
    if super_model_element.reversible:
        if process_direction == momapy.core.elements.Direction.HORIZONTAL:
            if float(sbgnml_production_arc.start.get("x")) > float(
                super_sbgnml_element.bbox.get("x")
            ):  # RIGHT
                model_element_cls = momapy.sbgn.pd.Product
            else:
                model_element_cls = momapy.sbgn.pd.Reactant  # LEFT
        else:
            if float(sbgnml_production_arc.start.get("y")) > float(
                super_sbgnml_element.bbox.get("y")
            ):  # TOP
                model_element_cls = momapy.sbgn.pd.Product
            else:
                model_element_cls = momapy.sbgn.pd.Reactant  # BOTTOM
    else:
        model_element_cls = momapy.sbgn.pd.Product
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_production_arc.get('id')}_model"
    target_model_element = reading_context.xml_id_to_model_element[sbgnml_target_id]
    model_element.element = target_model_element
    set_stoichiometry(model_element, sbgnml_stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_logical_operator(reading_context, sbgnml_logical_operator, model_element_cls):
    """Create a logical operator model builder.

    Args:
        reading_context: The reading context.
        sbgnml_logical_operator: The SBGN-ML logical operator element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A model element builder, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    sbgnml_id = sbgnml_logical_operator.get("id")
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_id}_model"
    return model_element


def make_logical_operator_input(
    reading_context, sbgnml_logic_arc, source_model_element
):
    """Create a frozen logical operator input model element.

    Args:
        reading_context: The reading context.
        sbgnml_logic_arc: The SBGN-ML logic arc element.
        source_model_element: The resolved source model element.

    Returns:
        A frozen model element, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    model_element = momapy.builder.new_builder_object(
        momapy.sbgn.pd.LogicalOperatorInput
    )
    model_element.id_ = f"{sbgnml_logic_arc.get('id')}_model"
    model_element.element = source_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_modulation(
    reading_context,
    sbgnml_modulation,
    model_element_cls,
    source_model_element,
    target_model_element,
):
    """Create a frozen modulation model element.

    Args:
        reading_context: The reading context.
        sbgnml_modulation: The SBGN-ML modulation arc element.
        model_element_cls: The model element class to instantiate.
        source_model_element: The resolved source model element.
        target_model_element: The resolved target model element.

    Returns:
        A frozen model element, or None if reading_context.model is None.
    """
    if reading_context.model is None:
        return None
    model_element = momapy.builder.new_builder_object(model_element_cls)
    model_element.id_ = f"{sbgnml_modulation.get('id')}_model"
    model_element.source = source_model_element
    model_element.target = target_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element
