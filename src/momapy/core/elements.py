"""Base element classes for maps."""

import abc
import dataclasses
import typing_extensions
import enum
from momapy.drawing import drawing_elements_to_geometry
from momapy.drawing import DrawingElement
from momapy.geometry import Bbox
from momapy.geometry import CubicBezierCurve
from momapy.geometry import EllipticalArc
from momapy.geometry import Point
from momapy.geometry import QuadraticBezierCurve
from momapy.geometry import Segment
from momapy.utils import make_uuid4_as_str


class Direction(enum.Enum):
    """Direction of a layout element or axis.

    Encodes either an axis (horizontal or vertical) or one of the four cardinal
    orientations.
    """

    HORIZONTAL = 1
    VERTICAL = 2
    UP = 3
    RIGHT = 4
    DOWN = 5
    LEFT = 6


class HAlignment(enum.Enum):
    """Horizontal alignment of text or content.

    Selects how content is positioned along the horizontal axis.
    """

    LEFT = 1
    CENTER = 2
    RIGHT = 3


class VAlignment(enum.Enum):
    """Vertical alignment of text or content.

    Selects how content is positioned along the vertical axis.
    """

    TOP = 1
    CENTER = 2
    BOTTOM = 3


@dataclasses.dataclass(frozen=True, kw_only=True)
class MapElement:
    """Base class for map elements.

    Common ancestor of every model and layout element making up a map.
    """

    id_: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=make_uuid4_as_str,
        metadata={
            "description": """The id of the map element. This id is purely for the user to keep track
    of the element, it does not need to be unique and is not part of the
    identity of the element, i.e., it is not considered when testing for
    equality between two map elements or when hashing the map element"""
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelElement(MapElement):
    """Base class for model elements.

    Common ancestor of every element carrying the semantic information of a map.
    """

    def descendants(self) -> list["ModelElement"]:
        """Return every `ModelElement` reachable from `self`, excluding `self`.

        This reflectively walks the dataclass field-graph (i.e. *reference
        reachability*) across scalar `ModelElement` fields and
        `frozenset`/`tuple` containers, deduplicating by object identity. A
        model element referenced by several parents therefore appears once.

        Note the deliberate contrast with
        [`LayoutElement.descendants`][momapy.core.elements.LayoutElement.descendants],
        which instead walks the explicit `children()` tree (visual
        *containment*): there a layout element contained under two parents is
        reached through each, with no identity dedup.

        Returns:
            The list of reachable `ModelElement` instances in visit
            order, without `self`.
        """
        seen: set[int] = {id(self)}
        result: list[ModelElement] = []
        if dataclasses.is_dataclass(self):
            for field in dataclasses.fields(type(self)):
                _walk_model_graph(getattr(self, field.name), seen, result)
        return result


def _walk_model_graph(
    value: object,
    seen: set[int],
    result: list[ModelElement],
) -> None:
    """Traverse a model-graph value, appending `ModelElement`s to `result`.

    Dedup is by object identity (`id()`).  Walks scalar `ModelElement`
    fields and `frozenset`/`tuple` containers.  Non-`ModelElement`
    scalars and other field types are ignored.

    Args:
        value: The value to traverse.  May be a `ModelElement`, a
            `frozenset`/`tuple` of values, or anything else (ignored).
        seen: Set of object ids already visited, updated in place.
        result: List of visited `ModelElement`s, appended in place.
    """
    if isinstance(value, ModelElement):
        if id(value) in seen:
            return
        seen.add(id(value))
        result.append(value)
        if not dataclasses.is_dataclass(value):
            return
        for field in dataclasses.fields(type(value)):
            _walk_model_graph(getattr(value, field.name), seen, result)
    elif isinstance(value, (frozenset, tuple)):
        for item in value:
            _walk_model_graph(item, seen, result)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LayoutElement(MapElement, abc.ABC):
    """Abstract base class for layout elements.

    Common ancestor of every element carrying the visual information of a map.
    """

    @abc.abstractmethod
    def bbox(self) -> Bbox:
        """Compute and return the bounding box of the layout element"""
        pass

    @abc.abstractmethod
    def drawing_elements(self) -> list[DrawingElement]:
        """Return the drawing elements of the layout element"""
        pass

    @abc.abstractmethod
    def children(self) -> list["LayoutElement"]:
        """Return the children of the layout element"""
        pass

    @abc.abstractmethod
    def childless(self) -> typing_extensions.Self:
        """Return a copy of the layout element with no children"""
        pass

    def descendants(self) -> list["LayoutElement"]:
        """Return the descendants of the layout element.

        This walks the explicit `children()` tree (i.e. visual
        *containment*) depth-first, returning every layout element in the
        contained subtree (without `self`).

        Note the deliberate contrast with
        [`ModelElement.descendants`][momapy.core.elements.ModelElement.descendants]
        and [`Model.descendants`][momapy.core.model.Model.descendants],
        which reflectively walk the dataclass field-graph (i.e. *reference
        reachability*) and deduplicate by object identity. A model element
        referenced by several parents therefore appears once across the
        model graph, whereas layout descendants are strictly the contained
        subtree and a layout element contained under two parents is reached
        through each.

        Returns:
            The list of descendant layout elements in visit order.
        """
        descendants = []
        for child in self.children():
            descendants.append(child)
            descendants += child.descendants()
        return descendants

    def flattened(self) -> list["LayoutElement"]:
        """Return a list containing copy of the layout element with no children and all its descendants with no children"""
        flattened = [self.childless()]
        for child in self.children():
            flattened += child.flattened()
        return flattened

    def equals(
        self, other: "LayoutElement", flattened: bool = False, unordered: bool = False
    ) -> bool:
        """Return `True` if the layout element is equal to another layout element, `False` otherwise"""
        if type(self) is type(other):
            if not flattened:
                return self == other
            else:
                if not unordered:
                    return self.flattened() == other.flattened()
                else:
                    return set(self.flattened()) == set(other.flattened())
        return False

    def contains(self, other: "LayoutElement") -> bool:
        """Return `True` if another layout element is a descendant of the layout element, `False` otherwise"""
        return other in self.descendants()

    def to_geometry(
        self,
    ) -> list[Segment | QuadraticBezierCurve | CubicBezierCurve | EllipticalArc]:
        """Return a list of geometry primitives from the drawing elements."""
        return drawing_elements_to_geometry(self.drawing_elements())

    def anchor_point(self, anchor_name: str) -> Point:
        """Return an anchor point of the layout element"""
        return getattr(self, anchor_name)()
