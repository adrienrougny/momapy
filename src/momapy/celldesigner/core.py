import dataclasses
import typing
import enum
import math

import momapy.core
import momapy.geometry
import momapy.meta.shapes
import momapy.meta.nodes
import momapy.meta.arcs
import momapy.sbml.core
import momapy.sbgn.core


@dataclasses.dataclass(frozen=True)
class CellDesignerModelElement(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: str | None = None


class ModificationState(enum.Enum):
    PHOSPHORYLATED = "P"
    UBIQUITINATED = "Ub"
    METHYLATED = "M"
    HYDROXYLATED = "OH"
    GLYCOSYLATED = "G"
    MYRISTOYLATED = "My"
    PALMITOYLATED = "Pa"
    PRENYLATED = "Pr"
    PROTONATED = "H"
    SULFATED = "S"
    DON_T_CARE = "*"
    UNKNOWN = "?"


@dataclasses.dataclass(frozen=True)
class Region(CellDesignerModelElement):
    name: str | None = None
    active: bool = False


@dataclasses.dataclass(frozen=True)
class ModificationSite(Region):
    pass


@dataclasses.dataclass(frozen=True)
class CodingRegion(Region):
    pass


@dataclasses.dataclass(frozen=True)
class RegulatoryRegion(Region):
    pass


@dataclasses.dataclass(frozen=True)
class TranscriptionStartingSiteL(Region):
    pass


@dataclasses.dataclass(frozen=True)
class TranscriptionStartingSiteR(Region):
    pass


@dataclasses.dataclass(frozen=True)
class ProteinBindingDomain(Region):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerSpeciesReference(CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class ProteinReference(CellDesignerSpeciesReference):
    name: str | None = None
    modification_residues: frozenset[ModificationResidue] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class GenericProteinReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class TruncatedProteinReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class ReceptorReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class IonChannelReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class GeneReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        RegulatoryRegion,
        TranscriptionStartingSiteL,
        TranscriptionStartingSiteR,
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class RNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class AntisenseRNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class Modification(CellDesignerModelElement):
    residue: ModificationResidue | None = None
    state: ModificationState | None = None


@dataclasses.dataclass(frozen=True)
class StructuralStateValue(enum.Enum):
    EMPTY = "empty"
    OPEN = "open"
    CLOSED = "closed"


@dataclasses.dataclass(frozen=True)
class StructuralState(CellDesignerModelElement):
    value: typing.Optional[typing.Union[StructuralStateValue, str]] = None


@dataclasses.dataclass(frozen=True)
class Compartment(momapy.sbml.core.Compartment, CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class Species(momapy.sbml.core.Species, CellDesignerModelElement):
    reference: CellDesignerSpeciesReference | None = None
    active: bool | None = None
    homodimer: int | None = 1


@dataclasses.dataclass(frozen=True)
class Protein(Species):
    reference: ProteinReference | None = None
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )
    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class GenericProtein(Protein):
    reference: GenericProteinReference | None = None


@dataclasses.dataclass(frozen=True)
class TruncatedProtein(Protein):
    reference: TruncatedProteinReference | None = None


@dataclasses.dataclass(frozen=True)
class Receptor(Protein):
    reference: ReceptorReference | None = None


@dataclasses.dataclass(frozen=True)
class IonChannel(Protein):
    reference: IonChannelReference | None = None


@dataclasses.dataclass(frozen=True)
class Gene(Species):
    reference: GeneReference | None = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class RNA(Species):
    reference: RNAReference | None = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class AntisenseRNA(Species):
    reference: AntisenseRNAReference | None = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class Phenotype(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class Ion(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class SimpleMolecule(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class Drug(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class Unknown(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class Complex(Species):
    name: str | None = None
    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Species] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class Degraded(Species):
    name: str | None = None


@dataclasses.dataclass(frozen=True)
class Reactant(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class Product(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class BooleanLogicGate(CellDesignerModelElement):
    inputs: frozenset[Species] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class AndGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class OrGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class NotGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class Modifier(
    momapy.sbml.core.ModifierSpeciesReference, CellDesignerModelElement
):
    species: Species | BooleanLogicGate | None = None


@dataclasses.dataclass(frozen=True)
class Modulator(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class Inhibitor(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulator(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class Catalyzer(PhysicalStimulator):
    pass


@dataclasses.dataclass(frozen=True)
class Trigger(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalyzer(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibitor(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class Reaction(momapy.sbml.core.Reaction, CellDesignerModelElement):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)
    modifiers: frozenset[Modifier] = dataclasses.field(
        default_factory=frozenset
    )
    ungrouped_modifiers: frozenset[Modifier] = dataclasses.field(
        default_factory=frozenset, compare=False, hash=False
    )


@dataclasses.dataclass(frozen=True)
class StateTransition(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class KnownTransitionOmitted(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownTransition(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Transcription(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Translation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Transport(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class HeterodimerAssociation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Dissociation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Truncation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class ModulationReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class InhibitionReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulationReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class CatalysisReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class TriggeringReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalysisReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibitionReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class BooleanLogicGateReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class ReactionModification(CellDesignerModelElement):
    source: typing.Optional[typing.Union[Species, BooleanLogicGate]] = None
    target: Species | None = None


@dataclasses.dataclass(frozen=True)
class Modulation(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class Inhibition(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulation(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class Catalysis(PhysicalStimulation):
    pass


@dataclasses.dataclass(frozen=True)
class Triggering(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalysis(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibition(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerNode(momapy.sbgn.core.SBGNNode):
    pass


@dataclasses.dataclass(frozen=True)
class _SimpleMixin(momapy.sbgn.core._SimpleMixin):
    pass


@dataclasses.dataclass(frozen=True)
class _MultiMixin(momapy.sbgn.core._MultiMixin):
    n: int = 1

    @property
    def _n(self):
        return self.n


@dataclasses.dataclass(frozen=True)
class GenericProteinLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.sbgn.MacromoleculeMultimerLayout._make_subunit_shape(
            self, position, width, height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _IonChannelShape(momapy.core.Shape):
    right_rectangle_width: float
    rounded_corners: float

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint9(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width + self.rounded_corners,
            self.height / 2,
        )

    def joint10(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            -self.height / 2,
        )

    def joint11(self):
        return self.position + (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint12(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint13(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint14(self):
        return self.position + (
            self.rounded_corners + self.width / 2 - self.right_rectangle_width,
            self.height / 2,
        )

    def joint15(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint16(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def border_drawing_element(self):
        left_rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width - self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        right_rectangle = momapy.drawing.Rectangle(
            point=self.position
            + (self.width / 2 - self.right_rectangle_width, -self.height / 2),
            height=self.height,
            width=self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        return [left_rectangle, right_rectangle]


@dataclasses.dataclass(frozen=True)
class IonChannelLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0
    right_rectangle_width: float = 20.0

    def _make_subunit_shape(self, position, width, height):
        return _IonChannelShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            right_rectangle_width=self.right_rectangle_width,
        )


@dataclasses.dataclass(frozen=True)
class ComplexLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 6.0
    # label -12 from south

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.cut_corners,
            top_left_ry=self.cut_corners,
            top_left_rounded_or_cut="cut",
            top_right_rx=self.cut_corners,
            top_right_ry=self.cut_corners,
            top_right_rounded_or_cut="cut",
            bottom_left_rx=self.cut_corners,
            bottom_left_ry=self.cut_corners,
            bottom_left_rounded_or_cut="cut",
            bottom_right_rx=self.cut_corners,
            bottom_right_ry=self.cut_corners,
            bottom_right_rounded_or_cut="cut",
        )


@dataclasses.dataclass(frozen=True)
class SimpleMoleculeLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shape.Ellipse(
            position=position, width=width, height=height
        )


@dataclasses.dataclass(frozen=True)
class IonLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shape.Ellipse(
            position=position, width=width, height=height
        )


@dataclasses.dataclass(frozen=True)
class UnknownLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.gray
    )

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shape.Ellipse(
            position=position, width=width, height=height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DegradedShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float

    def drawing_elements(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        actions = [
            momapy.drawing.MoveTo(
                self.position - (self.width / 2, -self.height / 2)
            ),
            momapy.drawing.LineTo(
                self.position + (self.width / 2, -self.height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True)
class DegradedLayout(_MultiMixin, CellDesignerNode):
    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return _DegradedShape(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True)
class GeneLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shape.Rectangle(
            position=position, width=width, height=height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=self.angle,
            right_angle=self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNALayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Parallelogram(
            position=position, width=width, height=height, angle=self.angle
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNALayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Parallelogram(
            position=position,
            width=width,
            height=height,
            angle=180 - self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TruncatedProteinShape(momapy.core.Shape):
    rounded_corners: float
    vertical_truncation: float  # proportion of total height, number in ]0, 1[
    horizontal_truncation: float  # proportion of total width number in ]0, 1[

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.vertical_truncation * self.height - self.height / 2,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def border_drawing_element(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint6()),
            momapy.drawing.EllipticalArc(
                self.joint7(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(self.joint8()),
            momapy.drawing.EllipticalArc(
                self.joint1(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        border = momapy.drawing.Path(actions=actions)
        return [border]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 8.0
    vertical_truncation: float = 0.40
    horizontal_truncation: float = 0.20

    def _make_subunit_shape(self, position, width, height):
        return _TruncatedProteinShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            vertical_truncation=self.vertical_truncation,
            horizontal_truncation=self.horizontal_truncation,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    vertical_truncation: float = (
        0.20  # proportion of total height, number in ]0, 1[
    )

    def _make_subunit_shape(self, position, width, height):
        angle = math.atan2(self.vertical_truncation * height, width / 2)
        angle = momapy.geometry.get_normalized_angle(angle)
        angle = math.degrees(angle)
        return momapy.meta.shapes.TurnedHexagon(
            position=position,
            width=width,
            height=height,
            top_angle=180 - angle,
            bottom_angle=angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DrugShape(momapy.core.Shape):
    horizontal_proportion: float  # ]0, 0.5[
    sep: float

    def joint1(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def joint4(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.EllipticalArc(
                self.joint3(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.EllipticalArc(
                self.joint1(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        outer_stadium = momapy.drawing.Path(actions=actions)
        inner_joint1 = self.joint1() + (0, self.sep)
        inner_joint2 = self.joint2() + (0, self.sep)
        inner_joint3 = self.joint3() + (0, -self.sep)
        inner_joint4 = self.joint4() + (0, -self.sep)
        inner_rx = self.horizontal_proportion * self.width - self.sep
        inner_ry = self.height / 2 - self.sep
        actions = [
            momapy.drawing.MoveTo(inner_joint1),
            momapy.drawing.LineTo(inner_joint2),
            momapy.drawing.EllipticalArc(
                inner_joint3,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(inner_joint4),
            momapy.drawing.EllipticalArc(
                inner_joint1,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        inner_stadium = momapy.drawing.Path(actions=actions)
        return [outer_stadium, inner_stadium]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrugLayout(_MultiMixin, CellDesignerNode):
    width: float = 60.0
    height: float = 30.0
    horizontal_proportion: float = 0.20
    sep: float = 4.0

    def _make_subunit_shape(self, position, width, height):
        return _DrugShape(
            position=position,
            width=width,
            height=height,
            horizontal_proportion=self.horizontal_proportion,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralStateLayout(_SimpleMixin, CellDesignerNode):
    width: float = 50.0
    height: float = 16.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationLayout(_SimpleMixin, CellDesignerNode):
    width: float = 16.0
    height: float = 16.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OvalCompartmentShape(momapy.core.Shape):
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        None
    )
    inner_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    inner_stroke_width: float | None = None
    sep: float = 12.0

    def border_drawing_elements(self):
        outer_oval = momapy.drawing.Ellipse(
            point=self.position,
            rx=self.width / 2,
            ry=self.height / 2,
        )
        inner_oval = momapy.drawing.Ellipse(
            fill=self.inner_fill,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        return [outer_oval, inner_oval]


@dataclasses.dataclass(frozen=True, kw_only=True)
class OvalCompartmentLayout(_SimpleMixin, CellDesignerNode):
    height: float = 16.0
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    inner_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    inner_stroke_width: float | None = 1.0
    sep: float = 12.0
    width: float = 16.0

    def _make_shape(self):
        return _OvalCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            width=self.width,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _RectangleCompartmentShape(momapy.core.Shape):
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        None
    )
    inner_rounded_corners: float = 10.0
    inner_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    inner_stroke_width: float | None = None
    rounded_corners: float = 10.0
    sep: float = 12.0

    def border_drawing_elements(self):
        outer_rectangle = momapy.drawing.Rectangle(
            point=self.position,
            height=self.height,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
            width=self.width,
        )
        inner_rectangle = momapy.drawing.Rectangle(
            fill=self.inner_fill,
            height=self.height - self.sep,
            point=self.position,
            rx=self.inner_rounded_corners,
            ry=self.inner_rounded_corners,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            width=self.width - self.sep,
        )
        return [outer_rectangle, inner_rectangle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class RectangleCompartmentLayout(_SimpleMixin, CellDesignerNode):
    width: float = 16.0
    height: float = 16.0
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    inner_rounded_corners: float = 10.0
    inner_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    inner_stroke_width: float | None = 1.0
    rounded_corners: float = 10.0
    sep: float = 12.0

    def _make_shape(self):
        return _RectangleCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_rounded_corners=self.inner_rounded_corners,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            rounded_corners=self.rounded_corners,
            sep=self.sep,
            width=self.width,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReactionNode(_SimpleMixin, CellDesignerNode):
    _shape_cls: typing.ClassVar[type] = momapy.meta.nodes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 8.0
    height: float = 8.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: float | None = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: float | None = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReactionLayout(momapy.meta.arcs.Triangle):
    reaction_node: ReactionNode

    def self_children(self):
        layout_elements = momapy.arcs.Triangle.self_children(self)
        layout_elements.append(self.reaction_node)
        return layout_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransitionLayout(ReactionLayout):
    width: float = 14.0
    height: float = 10.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: float | None = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: float | None = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionLayout(ReactionLayout):
    width: float = 12.0
    height: float = 12.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = (10, 3, 2, 3, 2, 3)
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: float | None = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: float | None = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.meta.arcs.PolyLine):
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: float | None = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: float | None = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.meta.arcs.Triangle):
    width: float = 14.0
    height: float = 10.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: float | None = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: float | None = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True)
class CellDesignerModel(momapy.sbml.core.Model):
    species_references: frozenset[CellDesignerSpeciesReference] = (
        dataclasses.field(default_factory=frozenset)
    )
    sbml_reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )
    boolean_logic_gates: frozenset[BooleanLogicGate] = dataclasses.field(
        default_factory=frozenset
    )
    modulations: frozenset[ReactionModification] = dataclasses.field(
        default_factory=frozenset
    )

    def is_submodel(self, other):
        pass


@dataclasses.dataclass(frozen=True)
class CellDesignerLayout(momapy.core.Layout):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerMap(momapy.core.Map):
    model: CellDesignerModel | None = None
    layout: CellDesignerLayout | None = None


CellDesignerModelBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerModel
)
CellDesignerLayoutBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerLayout
)


def _celldesigner_map_builder_new_model(self, *args, **kwargs):
    return CellDesignerModelBuilder(*args, **kwargs)


def _celldesigner_map_builder_new_layout(self, *args, **kwargs):
    return CellDesignerLayoutBuilder(*args, **kwargs)


CellDesignerMapBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerMap,
    builder_namespace={
        "new_model": _celldesigner_map_builder_new_model,
        "new_layout": _celldesigner_map_builder_new_layout,
    },
)
