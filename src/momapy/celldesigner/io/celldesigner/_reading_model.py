"""CellDesigner model-building functions.

Each ``make_*`` function takes a ``reading_context`` as its first
argument, checks whether ``reading_context.model`` is ``None``, and
returns ``None`` early when no model is being built.
"""

import frozendict

from momapy.celldesigner.io.celldesigner._reading_parsing import (
    get_notes,
    get_products,
    get_rdf,
    get_rdf_from_notes,
    get_reactants,
    get_template_from_species,
    make_name,
)

from momapy.sbml.io.sbml._model import make_annotations, make_notes
from momapy.sbml.io.sbml._qualifiers import QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER
from momapy.celldesigner.map import CellDesignerMapBuilder, CellDesignerModelBuilder
from momapy.celldesigner.model import (
    BooleanLogicGateInput,
    Compartment,
    Modification,
    ModificationResidue,
    Product,
    Reactant,
    StructuralState,
)


def make_annotations_from_element(cd_element):
    """Extract RDF annotations from a CellDesigner XML element.

    Args:
        cd_element: The CellDesigner XML element.

    Returns:
        List of annotations (empty if no RDF block).
    """
    cd_rdf = get_rdf(cd_element)
    if cd_rdf is None:
        return []
    return make_annotations(cd_rdf)


def make_annotations_from_notes(cd_notes):
    """Extract RDF annotations embedded in an SBML notes element.

    Args:
        cd_notes: The SBML notes XML element.

    Returns:
        List of annotations (empty if the notes contain no RDF).
    """
    cd_rdf = get_rdf_from_notes(cd_notes)
    if cd_rdf is None:
        return []
    return make_annotations(cd_rdf)


def make_notes_from_element(cd_element):
    """Extract the notes block from a CellDesigner XML element.

    Args:
        cd_element: The CellDesigner XML element.

    Returns:
        The parsed notes, or an empty notes object if absent.
    """
    cd_notes = get_notes(cd_element)
    return make_notes(cd_notes)


def make_and_add_annotations(reading_context, cd_element, model_element):
    """Add annotations from an XML element to the reading context.

    Args:
        reading_context: The reading context.
        cd_element: The CellDesigner XML element.
        model_element: The frozen model element to associate with.
    """
    if reading_context.with_annotations:
        annotations = make_annotations_from_element(cd_element)
        if annotations:
            reading_context.element_to_annotations[model_element].update(annotations)


def make_empty_model(cd_element):
    """Create an empty CellDesigner model builder.

    Args:
        cd_element: The root CellDesigner XML element (unused, kept for symmetry).

    Returns:
        A new empty CellDesigner model builder.
    """
    model = CellDesignerModelBuilder()
    return model


def make_empty_map(cd_element):
    """Create an empty CellDesigner map builder.

    Args:
        cd_element: The root CellDesigner XML element. Its ``id`` attribute,
            if present, is copied to the map builder.

    Returns:
        A new empty CellDesigner map builder.
    """
    map_ = CellDesignerMapBuilder()
    cd_map_id = cd_element.get("id")
    if cd_map_id is not None:
        map_.id_ = cd_map_id
    return map_


def make_compartment(reading_context, cd_compartment):
    """Create a compartment model builder from a CellDesigner compartment.

    Args:
        reading_context: The reading context.
        cd_compartment: The CellDesigner compartment XML element.

    Returns:
        A compartment model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Compartment)
    model_element.id_ = cd_compartment.get("id")
    model_element.name = make_name(cd_compartment.get("name"))
    model_element.metaid = cd_compartment.get("metaid")
    return model_element


def make_species_template(reading_context, cd_species_template, model_element_cls):
    """Create a species template model builder.

    Args:
        reading_context: The reading context.
        cd_species_template: The CellDesigner species template XML element.
        model_element_cls: The model element class to instantiate.

    Returns:
        A species template model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_species_template.get("id")
    model_element.name = make_name(cd_species_template.get("name"))
    return model_element


def make_modification_residue(
    reading_context, cd_modification_residue, super_cd_element, order
):
    """Create a modification residue model builder.

    Args:
        reading_context: The reading context.
        cd_modification_residue: The CellDesigner modification residue XML element.
        super_cd_element: The parent template XML element, used to compose a
            globally unique residue id.
        order: The residue index within its parent template.

    Returns:
        A modification residue model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(ModificationResidue)
    cd_modification_residue_id = (
        f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
    )
    model_element.id_ = cd_modification_residue_id
    model_element.name = make_name(cd_modification_residue.get("name"))
    model_element.order = order
    return model_element


def make_region(reading_context, cd_region, model_element_cls, super_cd_element, order):
    """Create a region model builder.

    Args:
        reading_context: The reading context.
        cd_region: The CellDesigner region XML element.
        model_element_cls: The model element class to instantiate.
        super_cd_element: The parent template XML element, used to compose a
            globally unique region id.
        order: The region index within its parent template.

    Returns:
        A region model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    cd_region_id = f"{super_cd_element.get('id')}_{cd_region.get('id')}"
    model_element.id_ = cd_region_id
    model_element.name = make_name(cd_region.get("name"))
    active = cd_region.get("active")
    if active is not None:
        model_element.active = True if active == "true" else False
    model_element.order = order
    return model_element


def make_species(
    reading_context,
    cd_species,
    model_element_cls,
    name,
    homomultimer,
    hypothetical,
    active,
):
    """Create a species model builder.

    Args:
        reading_context: The reading context.
        cd_species: The CellDesigner species XML element.
        model_element_cls: The model element class to instantiate.
        name: The species display name.
        homomultimer: Multimer count (``1`` if not a multimer).
        hypothetical: Whether the species is marked hypothetical.
        active: Whether the species is active.

    Returns:
        A species model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_species.get("id")
    model_element.name = name
    model_element.metaid = cd_species.get("metaid")
    cd_compartment_id = cd_species.get("compartment")
    if cd_compartment_id is not None:
        compartment_model_element = reading_context.xml_id_to_model_element[
            cd_compartment_id
        ]
        model_element.compartment = compartment_model_element
    cd_species_template = get_template_from_species(
        cd_species, reading_context.xml_id_to_xml_element
    )
    if cd_species_template is not None:
        model_element.template = reading_context.xml_id_to_model_element[
            cd_species_template.get("id")
        ]
    model_element.homomultimer = homomultimer
    model_element.hypothetical = hypothetical
    model_element.active = active
    return model_element


def make_species_modification(
    reading_context, modification_state, cd_modification_residue_id
):
    """Create a species modification model builder.

    Args:
        reading_context: The reading context.
        modification_state: The modification state (e.g. ``"phosphorylated"``).
        cd_modification_residue_id: The composite id of the target residue.

    Returns:
        A modification model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Modification)
    modification_residue_model_element = reading_context.xml_id_to_model_element[
        cd_modification_residue_id
    ]
    model_element.residue = modification_residue_model_element
    model_element.state = modification_state
    return model_element


def make_species_structural_state(reading_context, cd_species_structural_state):
    """Create a species structural state model builder.

    Args:
        reading_context: The reading context.
        cd_species_structural_state: The CellDesigner structural state XML element.

    Returns:
        A structural state model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(StructuralState)
    model_element.value = cd_species_structural_state.get("structuralState")
    return model_element


def make_reaction(reading_context, cd_reaction, model_element_cls):
    """Create a reaction model builder.

    Args:
        reading_context: The reading context.
        cd_reaction: The CellDesigner reaction XML element.
        model_element_cls: The reaction model element class to instantiate.

    Returns:
        A reaction model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.reversible = cd_reaction.get("reversible") == "true"
    return model_element


def make_reactant_from_base(reading_context, cd_base_reactant, cd_reaction):
    """Create a reactant model builder from a base reactant XML element.

    Args:
        reading_context: The reading context.
        cd_base_reactant: The CellDesigner base reactant XML element.
        cd_reaction: The enclosing reaction XML element, used to locate the
            matching SBML ``speciesReference`` for id/stoichiometry.

    Returns:
        A reactant model builder with ``base=True``, or ``None`` if no model
        is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Reactant)
    model_element.base = True
    cd_species_id = cd_base_reactant.get("species")
    for cd_reactant in get_reactants(cd_reaction):
        if cd_reactant.get("species") == cd_species_id:
            model_element.id_ = cd_reactant.get("metaid")
            cd_stoichiometry = cd_reactant.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = reading_context.xml_id_to_model_element[
        cd_base_reactant.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_reactant_from_link(reading_context, cd_reactant_link, cd_reaction):
    """Create a reactant model builder from a reactant link XML element.

    Args:
        reading_context: The reading context.
        cd_reactant_link: The CellDesigner reactant link XML element.
        cd_reaction: The enclosing reaction XML element, used to locate the
            matching SBML ``speciesReference`` for id/stoichiometry.

    Returns:
        A reactant model builder (non-base), or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Reactant)
    cd_species_id = cd_reactant_link.get("reactant")
    for cd_reactant in get_reactants(cd_reaction):
        if cd_reactant.get("species") == cd_species_id:
            model_element.id_ = cd_reactant.get("metaid")
            cd_stoichiometry = cd_reactant.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = reading_context.xml_id_to_model_element[
        cd_reactant_link.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_base(reading_context, cd_base_product, cd_reaction):
    """Create a product model builder from a base product XML element.

    Args:
        reading_context: The reading context.
        cd_base_product: The CellDesigner base product XML element.
        cd_reaction: The enclosing reaction XML element, used to locate the
            matching SBML ``speciesReference`` for id/stoichiometry.

    Returns:
        A product model builder with ``base=True``, or ``None`` if no model
        is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Product)
    model_element.base = True
    cd_species_id = cd_base_product.get("species")
    for cd_product in get_products(cd_reaction):
        if cd_product.get("species") == cd_species_id:
            model_element.id_ = cd_product.get("metaid")
            cd_stoichiometry = cd_product.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = reading_context.xml_id_to_model_element[
        cd_base_product.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_link(reading_context, cd_product_link, cd_reaction):
    """Create a product model builder from a product link XML element.

    Args:
        reading_context: The reading context.
        cd_product_link: The CellDesigner product link XML element.
        cd_reaction: The enclosing reaction XML element, used to locate the
            matching SBML ``speciesReference`` for id/stoichiometry.

    Returns:
        A product model builder (non-base), or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(Product)
    cd_species_id = cd_product_link.get("product")
    for cd_product in get_products(cd_reaction):
        if cd_product.get("species") == cd_species_id:
            model_element.id_ = cd_product.get("metaid")
            cd_stoichiometry = cd_product.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = reading_context.xml_id_to_model_element[
        cd_product_link.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_modifier(reading_context, model_element_cls, source_model_element, metaid):
    """Create a modifier model builder.

    Args:
        reading_context: The reading context.
        model_element_cls: The modifier model element class to instantiate.
        source_model_element: The species model element referred to by the modifier.
        metaid: The SBML ``metaid`` of the modifier reference, used as id.

    Returns:
        A modifier model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.referred_species = source_model_element
    model_element.id_ = metaid
    model_element.metaid = metaid
    return model_element


def make_logic_gate(reading_context, model_element_cls):
    """Create a boolean logic gate model builder.

    Args:
        reading_context: The reading context.
        model_element_cls: The logic gate model element class to instantiate.

    Returns:
        A logic gate model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    return model_element


def make_logic_gate_input(reading_context, input_model_element):
    """Create a logic gate input model builder.

    Args:
        reading_context: The reading context.
        input_model_element: The species model element feeding the gate.

    Returns:
        A logic gate input model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(BooleanLogicGateInput)
    model_element.element = input_model_element
    return model_element


def make_modulation(
    reading_context,
    cd_reaction,
    model_element_cls,
    source_model_element,
    target_model_element,
):
    """Create a modulation model builder.

    CellDesigner encodes modulations as fake SBML reactions.

    Args:
        reading_context: The reading context.
        cd_reaction: The CellDesigner reaction XML element encoding the modulation.
        model_element_cls: The modulation model element class to instantiate.
        source_model_element: The source (modulator) model element.
        target_model_element: The target (modulated) model element.

    Returns:
        A modulation model builder, or ``None`` if no model is being built.
    """
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.source = source_model_element
    model_element.target = target_model_element
    return model_element
