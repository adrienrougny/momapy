"""Abstract base classes and mixins for SBGN model and layout elements."""

import abc
import dataclasses
import typing

import momapy.builder
import momapy.coloring
import momapy.core.elements
import momapy.core.layout
import momapy.drawing
import momapy.geometry


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNModelElement(momapy.core.elements.ModelElement):
    """Base class for all SBGN model elements.

    Provides the foundation for SBGN-specific model components.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAuxiliaryUnit(SBGNModelElement):
    """Base class for SBGN auxiliary units.

    Auxiliary units represent additional information or states
    associated with SBGN glyphs, such as compartments or tags.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNRole(SBGNModelElement):
    """Base class for SBGN roles.

    Roles define how elements participate in SBGN processes.

    Attributes:
        element: The SBGN model element that has this role.
    """

    element: SBGNModelElement


@dataclasses.dataclass(frozen=True)
class SBGNNode(momapy.core.layout.Node):
    """Base class for SBGN nodes (glyphs).

    SBGN nodes represent biological entities such as macromolecules,
    simple chemicals, or complexes in SBGN diagrams.

    Attributes:
        fill: Fill color for the node.
        stroke: Stroke color for the node border.
        stroke_width: Width of the node border.

    Examples:
        ```python
        node = SBGNNode(position=momapy.geometry.Point(100, 100))
        ```
    """

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    stroke_width: float | None = 1.25

    def _border_drawing_elements(self):
        """Generate drawing elements for the node border.

        Returns:
            List of drawing elements composing the border.
        """
        drawing_elements = []
        done_bases = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, _SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True)
class SBGNSingleHeadedArc(momapy.core.layout.SingleHeadedArc):
    """Base class for SBGN arcs with a single arrowhead.

    Single-headed arcs represent directional relationships in SBGN,
    such as stimulation or catalysis.

    Attributes:
        arrowhead_fill: Fill color for the arrowhead.
        arrowhead_stroke: Stroke color for the arrowhead border.
        arrowhead_stroke_width: Width of the arrowhead border.
        path_fill: Fill color for the arc path.
        path_stroke: Stroke color for the arc path.
        path_stroke_width: Width of the arc path.
    """

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    arrowhead_stroke_width: float | None = 1.25
    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    path_stroke_width: float | None = 1.25


@dataclasses.dataclass(frozen=True)
class SBGNDoubleHeadedArc(momapy.core.layout.DoubleHeadedArc):
    """Base class for SBGN arcs with arrowheads at both ends.

    Double-headed arcs represent reversible or bidirectional
    relationships in SBGN diagrams.

    Attributes:
        end_arrowhead_fill: Fill color for the end arrowhead.
        end_arrowhead_stroke: Stroke color for the end arrowhead border.
        end_arrowhead_stroke_width: Width of the end arrowhead border.
        path_fill: Fill color for the arc path.
        path_stroke: Stroke color for the arc path.
        path_stroke_width: Width of the arc path.
        start_arrowhead_fill: Fill color for the start arrowhead.
        start_arrowhead_stroke: Stroke color for the start arrowhead border.
        start_arrowhead_stroke_width: Width of the start arrowhead border.
    """

    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_width: float | None = 1.25
    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    path_stroke_width: float | None = 1.25
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.white
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_width: float | None = 1.25


@dataclasses.dataclass(frozen=True)
class _SBGNMixin(object):
    """Private mixin class for SBGN drawing element generation.

    Provides abstract interface for generating drawing elements
    in SBGN nodes and arcs.
    """

    @classmethod
    @abc.abstractmethod
    def _mixin_drawing_elements(cls, obj):
        """Generate drawing elements for this mixin.

        Args:
            obj: The object instance to generate elements for.

        Returns:
            List of drawing elements.
        """
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ConnectorsMixin(_SBGNMixin):
    """Private mixin for elements with connector lines.

    Provides support for left and right connector lines that extend
    from the main shape, used in SBGN process nodes.

    Attributes:
        direction: Orientation of connectors (HORIZONTAL or VERTICAL).
        left_to_right: Whether connectors flow left to right.
        left_connector_length: Length of the left connector.
        right_connector_length: Length of the right connector.
    """

    direction: momapy.core.elements.Direction = (
        momapy.core.elements.Direction.HORIZONTAL
    )
    left_to_right: bool = True
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    left_connector_stroke_width: float | None = None
    left_connector_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    left_connector_stroke_dashoffset: float | None = None
    left_connector_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        None
    )
    left_connector_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    left_connector_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    right_connector_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    right_connector_stroke_width: float | None = None
    right_connector_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    right_connector_stroke_dashoffset: float | None = None
    right_connector_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    right_connector_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    right_connector_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None

    def left_connector_base(self) -> momapy.geometry.Point:
        """Get the base point of the left connector.

        Returns:
            Point where the left connector attaches to the shape.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)
        else:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def right_connector_base(self) -> momapy.geometry.Point:
        """Get the base point of the right connector.

        Returns:
            Point where the right connector attaches to the shape.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)
        else:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def left_connector_tip(self) -> momapy.geometry.Point:
        """Get the tip point of the left connector.

        Returns:
            Point at the end of the left connector line.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height / 2 - self.left_connector_length
            )
        else:
            return momapy.geometry.Point(
                self.x - self.width / 2 - self.left_connector_length, self.y
            )

    def right_connector_tip(self) -> momapy.geometry.Point:
        """Get the tip point of the right connector.

        Returns:
            Point at the end of the right connector line.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height / 2 + self.right_connector_length
            )
        else:
            return momapy.geometry.Point(
                self.x + self.width / 2 + self.right_connector_length, self.y
            )

    def west(self) -> momapy.geometry.Point:
        """Get the west (left) anchor point.

        Returns:
            Point on the west side of the element.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width / 2 - self.left_connector_length, self.y
            )

    def south(self) -> momapy.geometry.Point:
        """Get the south (bottom) anchor point.

        Returns:
            Point on the south side of the element.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height / 2 + self.right_connector_length
            )
        else:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def east(self) -> momapy.geometry.Point:
        """Get the east (right) anchor point.

        Returns:
            Point on the east side of the element.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width / 2 + self.right_connector_length, self.y
            )

    def north(self) -> momapy.geometry.Point:
        """Get the north (top) anchor point.

        Returns:
            Point on the north side of the element.
        """
        if self.direction == momapy.core.elements.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height / 2 - self.left_connector_length
            )
        else:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        """Generate drawing elements for connectors.

        Args:
            obj: The object instance to generate elements for.

        Returns:
            List of drawing elements for the connector lines.
        """
        if obj.direction == momapy.core.elements.Direction.VERTICAL:
            left_actions = [
                momapy.drawing.MoveTo(obj.left_connector_base()),
                momapy.drawing.LineTo(
                    obj.left_connector_base() - (0, obj.left_connector_length)
                ),
            ]
            right_actions = [
                momapy.drawing.MoveTo(obj.right_connector_base()),
                momapy.drawing.LineTo(
                    obj.right_connector_base() + (0, obj.right_connector_length)
                ),
            ]
        else:
            left_actions = [
                momapy.drawing.MoveTo(obj.left_connector_base()),
                momapy.drawing.LineTo(
                    obj.left_connector_base() - (obj.left_connector_length, 0)
                ),
            ]
            right_actions = [
                momapy.drawing.MoveTo(obj.right_connector_base()),
                momapy.drawing.LineTo(
                    obj.right_connector_base() + (obj.right_connector_length, 0)
                ),
            ]
        path_left = momapy.drawing.Path(
            stroke=obj.left_connector_stroke,
            stroke_width=obj.left_connector_stroke_width,
            stroke_dasharray=obj.left_connector_stroke_dasharray,
            stroke_dashoffset=obj.left_connector_stroke_dashoffset,
            fill=obj.left_connector_fill,
            transform=obj.left_connector_transform,
            filter=obj.left_connector_filter,
            actions=left_actions,
        )
        path_right = momapy.drawing.Path(
            stroke=obj.right_connector_stroke,
            stroke_width=obj.right_connector_stroke_width,
            stroke_dasharray=obj.right_connector_stroke_dasharray,
            stroke_dashoffset=obj.right_connector_stroke_dashoffset,
            fill=obj.right_connector_fill,
            transform=obj.right_connector_transform,
            filter=obj.right_connector_filter,
            actions=right_actions,
        )
        return [path_left, path_right]


@dataclasses.dataclass(frozen=True)
class _SimpleMixin(_SBGNMixin):
    """Private mixin for simple single-shape SBGN nodes.

    Provides support for nodes that consist of a single geometric shape.
    """

    @abc.abstractmethod
    def _make_shape(self):
        """Create the shape for this node.

        Returns:
            Shape object representing the node's geometry.
        """
        pass

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        """Generate drawing elements for the shape.

        Args:
            obj: The object instance to generate elements for.

        Returns:
            List of drawing elements.
        """
        shape = obj._make_shape()
        drawing_elements = shape.drawing_elements()
        return drawing_elements


@dataclasses.dataclass(frozen=True)
class _MultiMixin(_SBGNMixin):
    """Private mixin for multi-unit SBGN nodes (multimers).

    Provides support for nodes composed of multiple stacked units,
    such as macromolecule multimers or complex multimers.

    Attributes:
        offset: Offset distance between stacked units.
        subunits_stroke: Tuple of stroke colors for each subunit.
        subunits_stroke_width: Tuple of stroke widths for each subunit.
        subunits_fill: Tuple of fill colors for each subunit.
    """

    _n: typing.ClassVar[int] = 2
    offset: float = 3.0
    subunits_stroke: (
        tuple[momapy.drawing.NoneValueType | momapy.coloring.Color] | None
    ) = None
    subunits_stroke_width: tuple[momapy.drawing.NoneValueType | float] | None = None
    subunits_stroke_dasharray: (
        tuple[momapy.drawing.NoneValueType | tuple[float]] | None
    ) = None
    subunits_stroke_dashoffset: tuple[float] | None = None
    subunits_fill: (
        tuple[momapy.drawing.NoneValueType | momapy.coloring.Color] | None
    ) = None
    subunits_transform: (
        tuple[momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation]]
        | None
    ) = None
    subunits_filter: (
        tuple[momapy.drawing.NoneValueType | momapy.drawing.Filter] | None
    ) = None

    @abc.abstractmethod
    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        """Create a single subunit shape.

        Args:
            position: Center position for the subunit.
            width: Width of the subunit.
            height: Height of the subunit.

        Returns:
            Shape object for the subunit.
        """
        pass

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        """Generate drawing elements for all subunits.

        Args:
            obj: The object instance to generate elements for.

        Returns:
            List of drawing elements for all stacked subunits.
        """
        drawing_elements = []
        width = obj.width - obj.offset * (obj._n - 1)
        height = obj.height - obj.offset * (obj._n - 1)
        for i in range(obj._n):
            position = obj.position + (
                obj.width / 2 - width / 2 - i * obj.offset,
                obj.height / 2 - height / 2 - i * obj.offset,
            )
            kwargs = {}
            for attr_name in [
                "stroke",
                "stroke_width",
                "stroke_dasharray",
                "stroke_dashoffset",
                "fill",
                "transform",
                "filter",
            ]:
                attr_value = getattr(obj, f"subunits_{attr_name}")
                if attr_value is not None and len(attr_value) > i:
                    kwargs[f"{attr_name}"] = attr_value[i]
            subunit_shape = obj._make_subunit_shape(position, width, height)
            kwargs["elements"] = subunit_shape.drawing_elements()
            group = momapy.drawing.Group(**kwargs)
            drawing_elements.append(group)
        return drawing_elements

    def label_center(self) -> momapy.geometry.Point:
        """Get the center position for the node label.

        Returns:
            Point where the label should be centered.
        """
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2 - (self._n - 1) * self.offset,
            self.height / 2 - height / 2 - (self._n - 1) * self.offset,
        )
        return self._make_subunit_shape(
            position=position, width=width, height=height
        ).position


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TextMixin(_SBGNMixin):
    """Private mixin for SBGN nodes with text labels.

    Provides support for rendering text labels on SBGN nodes,
    such as state variables or unit of information labels.

    Attributes:
        text: Text content to display.
        font_family: Font family for the text.
        font_style: Font style (normal, italic, etc.).
        font_weight: Font weight (normal, bold, etc.).
        font_fill: Fill color for the text.
        font_stroke: Stroke color for the text outline.
        _font_size_func: Function to calculate font size. Kept as a
            ``ClassVar`` because it is a computation rule rather than
            a style value and relies on descriptor binding.
    """

    _font_size_func: typing.ClassVar[typing.Callable]
    text: str = ""
    font_family: str = momapy.drawing.DEFAULT_FONT_FAMILY
    font_fill: momapy.coloring.Color | momapy.drawing.NoneValueType = (
        momapy.coloring.black
    )
    font_stroke: momapy.coloring.Color | momapy.drawing.NoneValueType = (
        momapy.drawing.NoneValue
    )
    font_style: momapy.drawing.FontStyle = momapy.drawing.FontStyle.NORMAL
    font_weight: momapy.drawing.FontWeight | float = momapy.drawing.FontWeight.NORMAL

    def _make_text_layout(self):
        """Create a text layout for the label.

        Returns:
            TextLayout object configured for this node's label.
        """
        text_layout = momapy.core.layout.TextLayout(
            text=self.text,
            position=self.label_center(),
            font_family=self.font_family,
            font_size=self._font_size_func(),
            font_style=self.font_style,
            font_weight=self.font_weight,
            fill=self.font_fill,
            stroke=self.font_stroke,
        )
        return text_layout

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        """Generate drawing elements for the text label.

        Args:
            obj: The object instance to generate elements for.

        Returns:
            List of drawing elements for the text.
        """
        return obj._make_text_layout().drawing_elements()
