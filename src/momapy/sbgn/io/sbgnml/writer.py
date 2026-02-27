"""SBGN-ML writer classes."""

import dataclasses
import typing

import lxml.etree

import momapy.core.elements
import momapy.core.layout
import momapy.io.core
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.io.sbgnml._qualifiers


@dataclasses.dataclass
class WritingContext:
    """Bundles the shared state passed across all writer methods."""

    map_: typing.Any
    annotations: dict
    notes: dict
    ids: dict
    with_annotations: bool
    with_notes: bool


class _SBGNMLWriter(momapy.io.core.Writer):
    _NSMAP = {
        None: "http://sbgn.org/libsbgn/0.3",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "bqmodel": "http://biomodels.net/model-qualifiers/",
        "bqbiol": "http://biomodels.net/biology-qualifiers/",
    }
    _DIRECTION_TO_SBGNML_ORIENTATION = {
        momapy.core.elements.Direction.HORIZONTAL: "horizontal",
        momapy.core.elements.Direction.VERTICAL: "vertical",
        momapy.core.elements.Direction.RIGHT: "right",
        momapy.core.elements.Direction.LEFT: "left",
        momapy.core.elements.Direction.DOWN: "down",
        momapy.core.elements.Direction.UP: "up",
    }
    _CLASS_TO_SBGNML_CLASS_ATTRIBUTE = {
        momapy.sbgn.pd.SBGNPDMap: "process description",
        momapy.sbgn.pd.SBGNPDModel: "process description",
        momapy.sbgn.pd.SBGNPDLayout: "process description",
        momapy.sbgn.pd.StateVariableLayout: "state variable",
        momapy.sbgn.pd.UnitOfInformationLayout: "unit of information",
        momapy.sbgn.pd.TerminalLayout: "terminal",
        momapy.sbgn.pd.MacromoleculeSubunitLayout: "macromolecule",
        momapy.sbgn.pd.SimpleChemicalSubunitLayout: "simple chemical",
        momapy.sbgn.pd.NucleicAcidFeatureSubunitLayout: "nucleic acid feature",
        momapy.sbgn.pd.ComplexSubunitLayout: "complex",
        momapy.sbgn.pd.MacromoleculeMultimerSubunitLayout: "macromolecule multimer",
        momapy.sbgn.pd.SimpleChemicalMultimerSubunitLayout: "simple chemical multimer",
        momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunitLayout: "nucleic acid feature multimer",
        momapy.sbgn.pd.ComplexMultimerSubunitLayout: "complex multimer",
        momapy.sbgn.pd.CompartmentLayout: "compartment",
        momapy.sbgn.pd.SubmapLayout: "submap",
        momapy.sbgn.pd.UnspecifiedEntityLayout: "unspecified entity",
        momapy.sbgn.pd.MacromoleculeLayout: "macromolecule",
        momapy.sbgn.pd.SimpleChemicalLayout: "simple chemical",
        momapy.sbgn.pd.NucleicAcidFeatureLayout: "nucleic acid feature",
        momapy.sbgn.pd.ComplexLayout: "complex",
        momapy.sbgn.pd.MacromoleculeMultimerLayout: "macromolecule multimer",
        momapy.sbgn.pd.SimpleChemicalMultimerLayout: "simple chemical multimer",
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout: "nucleic acid feature multimer",
        momapy.sbgn.pd.ComplexMultimerLayout: "complex multimer",
        momapy.sbgn.pd.PerturbingAgentLayout: "perturbing agent",
        momapy.sbgn.pd.EmptySetLayout: "empty set",
        momapy.sbgn.pd.TagLayout: "tag",
        momapy.sbgn.pd.GenericProcessLayout: "process",
        momapy.sbgn.pd.UncertainProcessLayout: "uncertain process",
        momapy.sbgn.pd.OmittedProcessLayout: "omitted process",
        momapy.sbgn.pd.AssociationLayout: "association",
        momapy.sbgn.pd.DissociationLayout: "dissociation",
        momapy.sbgn.pd.PhenotypeLayout: "phenotype",
        momapy.sbgn.pd.AndOperatorLayout: "and",
        momapy.sbgn.pd.OrOperatorLayout: "or",
        momapy.sbgn.pd.NotOperatorLayout: "not",
        momapy.sbgn.pd.EquivalenceOperatorLayout: "equivalence",
        momapy.sbgn.pd.ConsumptionLayout: "consumption",
        momapy.sbgn.pd.ProductionLayout: "production",
        momapy.sbgn.pd.ModulationLayout: "modulation",
        momapy.sbgn.pd.StimulationLayout: "stimulation",
        momapy.sbgn.pd.CatalysisLayout: "catalysis",
        momapy.sbgn.pd.NecessaryStimulationLayout: "necessary stimulation",
        momapy.sbgn.pd.InhibitionLayout: "inhibition",
        momapy.sbgn.pd.LogicArcLayout: "logic arc",
        momapy.sbgn.pd.EquivalenceArcLayout: "equivalence arc",
        momapy.sbgn.af.CompartmentLayout: "compartment",
        momapy.sbgn.af.SubmapLayout: "submap",
        momapy.sbgn.af.BiologicalActivityLayout: "biological activity",
        momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout: "unspecified entity",
        momapy.sbgn.af.MacromoleculeUnitOfInformationLayout: "macromolecule",
        momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout: "simple chemical",
        momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout: "nucleic acid feature",
        momapy.sbgn.af.ComplexUnitOfInformationLayout: "complex",
        momapy.sbgn.af.PerturbationUnitOfInformationLayout: "perturbation",
        momapy.sbgn.af.PhenotypeLayout: "phenotype",
        momapy.sbgn.af.AndOperatorLayout: "and",
        momapy.sbgn.af.OrOperatorLayout: "or",
        momapy.sbgn.af.NotOperatorLayout: "not",
        momapy.sbgn.af.DelayOperatorLayout: "delay",
        momapy.sbgn.af.UnknownInfluenceLayout: "unknown influence",
        momapy.sbgn.af.PositiveInfluenceLayout: "positive influence",
        momapy.sbgn.af.NecessaryStimulationLayout: "necessary stimulation",
        momapy.sbgn.af.NegativeInfluenceLayout: "negative influence",
        momapy.sbgn.af.TerminalLayout: "terminal",
        momapy.sbgn.af.TagLayout: "tag",
        momapy.sbgn.af.LogicArcLayout: "logic arc",
        momapy.sbgn.af.EquivalenceArcLayout: "equivalence arc",
    }

    @classmethod
    def _make_lxml_element(
        cls, tag, namespace=None, attributes=None, text=None, nsmap=None
    ):
        if namespace is not None:
            lxml_tag = f"{{{namespace}}}{tag}"
        else:
            lxml_tag = tag
        if nsmap is None:
            nsmap = {}
        if attributes is None:
            attributes = {}
        lxml_element = lxml.etree.Element(lxml_tag, nsmap=nsmap, **attributes)
        if text is not None:
            lxml_element.text = text
        return lxml_element

    @classmethod
    def _get_sbgnml_id_from_map_element(cls, map_element, ids):
        sbgnml_ids = ids.get(map_element)
        if sbgnml_ids is None:
            sbgnml_id = map_element.id_
        else:
            sbgnml_id = sbgnml_ids[0]
        return sbgnml_id

    @classmethod
    def write(
        cls,
        obj: momapy.sbgn.core.SBGNMap,
        file_path,
        annotations=None,
        notes=None,
        ids=None,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        if annotations is None:
            annotations = {}
        if notes is None:
            notes = {}
        if ids is None:
            ids = {}
        ctx = WritingContext(
            map_=obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        sbgnml_sbgn = cls._make_lxml_element("sbgn", nsmap=cls._NSMAP)
        sbgnml_map = cls._make_sbgnml_map_from_map(ctx)
        sbgnml_sbgn.append(sbgnml_map)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                lxml.etree.tostring(
                    sbgnml_sbgn, pretty_print=True, xml_declaration=True
                ).decode()
            )

    @classmethod
    def _make_sbgnml_map_from_map(cls, ctx):
        language = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(ctx.map_)]
        id_ = ctx.ids.get(ctx.map_)
        if id_ is None:
            id_ = ctx.map_.id_
        else:
            id_ = id_[0]
        attributes = {"id": id_, "language": language}
        sbgnml_map = cls._make_lxml_element("map", attributes=attributes)
        sbgnml_bbox = cls._make_sbgnml_bbox_from_node(ctx.map_.layout)
        sbgnml_map.append(sbgnml_bbox)
        for layout_element in ctx.map_.layout.layout_elements:
            cls._make_and_add_sbgnml_elements_from_layout_element(
                ctx=ctx,
                sbgnml_map=sbgnml_map,
                layout_element=layout_element,
            )
        return sbgnml_map

    @classmethod
    def _make_and_add_sbgnml_elements_from_layout_element(
        cls, ctx, sbgnml_map, layout_element
    ):
        model_element = ctx.map_.get_mapping(layout_element)
        if model_element is not None:
            if isinstance(layout_element, momapy.core.layout.Node):
                sbgnml_elements = cls._make_sbgnml_elements_from_node(
                    ctx=ctx,
                    node=layout_element,
                )
            elif isinstance(
                layout_element,
                (momapy.core.layout.SingleHeadedArc, momapy.core.layout.DoubleHeadedArc),
            ):
                sbgnml_elements = cls._make_sbgnml_elements_from_arc(
                    ctx=ctx,
                    arc=layout_element,
                )
            if ctx.with_annotations:
                if ctx.annotations is not None:
                    element_annotations = ctx.annotations.get(model_element)
                    if element_annotations is not None:
                        sbgnml_annotation = (
                            cls._make_sbgnml_annotation_from_annotations(
                                element_annotations,
                                sbgnml_id=cls._get_sbgnml_id_from_map_element(
                                    model_element, ctx.ids
                                ),
                            )
                        )
                        sbgnml_extension = cls._make_lxml_element("extension")
                        sbgnml_extension.append(sbgnml_annotation)
                        for sbgnml_element in sbgnml_elements:
                            sbgnml_element.append(sbgnml_extension)
            if ctx.with_notes:
                if ctx.notes is not None:
                    element_notes = ctx.notes.get(model_element)
                    if element_notes is not None:
                        sbgnml_notes = cls._make_lxml_element(tag="notes")
                        notes_root = lxml.etree.fromstring(element_notes)
                        sbgnml_notes.append(notes_root)
                        for sbgnml_element in sbgnml_elements:
                            sbgnml_element.append(sbgnml_notes)
            for sbgnml_element in sbgnml_elements:
                sbgnml_map.append(sbgnml_element)

    @classmethod
    def _make_sbgnml_annotation_from_annotations(cls, annotations, sbgnml_id):
        sbgnml_annotation = cls._make_lxml_element("annotation")
        sbgnml_rdf = cls._make_lxml_element(
            tag="RDF", namespace=cls._NSMAP["rdf"], nsmap=cls._NSMAP
        )
        sbgnml_annotation.append(sbgnml_rdf)
        sbgnml_description = cls._make_lxml_element(
            tag="Description",
            namespace=cls._NSMAP["rdf"],
            attributes={f"{{{cls._NSMAP['rdf']}}}about": f"#{sbgnml_id}"},
        )
        sbgnml_rdf.append(sbgnml_description)
        for annotation in annotations:
            namespace, tag = momapy.sbgn.io.sbgnml._qualifiers.QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
                annotation.qualifier
            ]
            sbgnml_bq = cls._make_lxml_element(tag=tag, namespace=namespace)
            sbgnml_description.append(sbgnml_bq)
            sbgnml_bag = cls._make_lxml_element(tag="Bag", namespace=cls._NSMAP["rdf"])
            sbgnml_bq.append(sbgnml_bag)
            for resource in annotation.resources:
                sbgnml_li = cls._make_lxml_element(
                    tag="li",
                    namespace=cls._NSMAP["rdf"],
                    attributes={f"{{{cls._NSMAP['rdf']}}}resource": resource},
                )
                sbgnml_bag.append(sbgnml_li)
        return sbgnml_annotation

    @classmethod
    def _make_sbgnml_elements_from_node(cls, ctx, node):
        sbgnml_id = cls._get_sbgnml_id_from_map_element(node, ctx.ids)
        sbgnml_class = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(node)]
        attributes = {"id": sbgnml_id, "class": sbgnml_class}
        direction = getattr(node, "direction", None)
        if direction is not None:
            sbgnml_orientation = cls._DIRECTION_TO_SBGNML_ORIENTATION[direction]
            attributes["orientation"] = sbgnml_orientation
        model_element = ctx.map_.get_mapping(node)
        if isinstance(
            model_element, (momapy.sbgn.pd.EntityPool, momapy.sbgn.af.Activity)
        ):
            compartment = model_element.compartment
            if compartment is not None:
                compartment_id = cls._get_sbgnml_id_from_map_element(compartment, ctx.ids)
                attributes["compartmentRef"] = compartment_id
        sbgnml_element = cls._make_lxml_element("glyph", attributes=attributes)
        sbgnml_elements = [sbgnml_element]
        sbgnml_bbox = cls._make_sbgnml_bbox_from_node(node)
        sbgnml_element.append(sbgnml_bbox)
        if node.label is not None:
            if isinstance(node, momapy.sbgn.pd.StateVariableLayout):
                sbgnml_state = cls._make_sbgnml_state_from_text_layout(node.label)
                sbgnml_element.append(sbgnml_state)
            else:
                sbgnml_label = cls._make_sbgnml_label_from_text_layout(node.label)
                sbgnml_element.append(sbgnml_label)
        for side, attr in [("left", "left_connector_tip"), ("right", "right_connector_tip")]:
            if hasattr(node, attr):
                connector_tip = getattr(node, attr)()
                sbgnml_port = cls._make_sbgnml_port_from_point(
                    connector_tip, port_id=f"{sbgnml_id}_{side}"
                )
                sbgnml_element.append(sbgnml_port)
        for layout_element in node.layout_elements:
            if isinstance(layout_element, momapy.core.layout.Node):
                sub_sbgnml_elements = cls._make_sbgnml_elements_from_node(
                    ctx=ctx,
                    node=layout_element,
                )
                for sub_sbgnml_element in sub_sbgnml_elements:
                    if sub_sbgnml_element.tag == "glyph":
                        sbgnml_element.append(sub_sbgnml_element)
                    else:
                        sbgnml_elements.append(sub_sbgnml_element)
        return sbgnml_elements

    @classmethod
    def _make_sbgnml_elements_from_arc(cls, ctx, arc):
        sbgnml_id = cls._get_sbgnml_id_from_map_element(arc, ctx.ids)
        sbgnml_class = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(arc)]
        attributes = {
            "id": sbgnml_id,
            "class": sbgnml_class,
        }
        points = arc.points()
        sbgnml_source_id = cls._get_sbgnml_id_from_map_element(arc.source, ctx.ids)
        sbgnml_target_id = cls._get_sbgnml_id_from_map_element(arc.target, ctx.ids)
        # momapy reverts the consumption and logic arc direction compared to
        # SBGN-ML, so we need to revert it back here
        if isinstance(
            arc,
            (
                momapy.sbgn.pd.ConsumptionLayout,
                momapy.sbgn.pd.LogicArcLayout,
                momapy.sbgn.af.LogicArcLayout,
                momapy.sbgn.pd.EquivalenceArcLayout,
                momapy.sbgn.af.EquivalenceArcLayout,
            ),
        ):
            attributes["source"] = sbgnml_target_id
            attributes["target"] = sbgnml_source_id
            points.reverse()
        else:
            attributes["target"] = sbgnml_target_id
            attributes["source"] = sbgnml_source_id
        sbgnml_element = cls._make_lxml_element("arc", attributes=attributes)
        sbgnml_points = cls._make_sbgnml_points_from_points(points)
        for sbgnml_point in sbgnml_points:
            sbgnml_element.append(sbgnml_point)
        return [sbgnml_element]

    @classmethod
    def _make_sbgnml_points_from_points(cls, points):
        sbgnml_elements = []
        start_point = points[0]
        sbgnml_start_point_attributes = {
            "x": str(start_point.x),
            "y": str(start_point.y),
        }
        sbgnml_start_point = cls._make_lxml_element(
            "start", attributes=sbgnml_start_point_attributes
        )
        sbgnml_elements.append(sbgnml_start_point)
        for point in points[1:-1]:
            sbgnml_next_point_attributes = {
                "x": str(point.x),
                "y": str(point.y),
            }
            sbgnml_next_point = cls._make_lxml_element(
                "next", attributes=sbgnml_next_point_attributes
            )
            sbgnml_elements.append(sbgnml_next_point)
        end_point = points[-1]
        sbgnml_end_point_attributes = {
            "x": str(end_point.x),
            "y": str(end_point.y),
        }
        sbgnml_end_point = cls._make_lxml_element(
            "end", attributes=sbgnml_end_point_attributes
        )
        sbgnml_elements.append(sbgnml_end_point)
        return sbgnml_elements

    @classmethod
    def _make_sbgnml_port_from_point(cls, point, port_id):
        attributes = {"id": port_id, "x": str(point.x), "y": str(point.y)}
        sbgnml_element = cls._make_lxml_element("port", attributes=attributes)
        return sbgnml_element

    @classmethod
    def _make_sbgnml_bbox_from_node(cls, node):
        attributes = {
            "x": str(node.x - node.width / 2),
            "y": str(node.y - node.height / 2),
            "w": str(node.width),
            "h": str(node.height),
        }
        sbgnml_bbox = cls._make_lxml_element("bbox", attributes=attributes)
        return sbgnml_bbox

    @classmethod
    def _make_sbgnml_bbox_from_text_layout(cls, text_layout):
        bbox = text_layout.bbox()
        attributes = {
            "x": str(bbox.x - bbox.width / 2),
            "y": str(bbox.y - bbox.height / 2),
            "w": str(bbox.width),
            "h": str(bbox.height),
        }
        sbgnml_bbox = cls._make_lxml_element("bbox", attributes=attributes)
        return sbgnml_bbox

    @classmethod
    def _make_sbgnml_label_from_text_layout(cls, text_layout):
        attributes = {"text": text_layout.text}
        sbgnml_label = cls._make_lxml_element("label", attributes=attributes)
        sbgnml_bbox = cls._make_sbgnml_bbox_from_text_layout(text_layout)
        sbgnml_label.append(sbgnml_bbox)
        return sbgnml_label

    @classmethod
    def _make_sbgnml_state_from_text_layout(cls, text_layout):
        attributes = {}
        text_split = text_layout.text.split("@")
        if len(text_split) > 1:
            attributes["variable"] = text_split[-1]
        if text_split[0]:
            attributes["value"] = text_split[0]
        sbgnml_state = cls._make_lxml_element("state", attributes=attributes)
        return sbgnml_state


class SBGNML0_3Writer(_SBGNMLWriter):
    """Class for SBGN-ML 0.3 writer objects"""

    pass
