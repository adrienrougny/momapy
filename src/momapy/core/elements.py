"""Base element classes for maps."""

import abc
import dataclasses
import typing_extensions
import enum
import shapely

import momapy.drawing
import momapy.geometry
import momapy.utils


class Direction(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    UP = 3
    RIGHT = 4
    DOWN = 5
    LEFT = 6


class HAlignment(enum.Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3


class VAlignment(enum.Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3


@dataclasses.dataclass(frozen=True, kw_only=True)
class MapElement:
    """Base class for map elements"""

    id_: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=momapy.utils.make_uuid4_as_str,
        metadata={
            "description": """The id of the map element. This id is purely for the user to keep track
    of the element, it does not need to be unique and is not part of the
    identity of the element, i.e., it is not considered when testing for
    equality between two map elements or when hashing the map element"""
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelElement(MapElement):
    """Base class for model elements"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LayoutElement(MapElement, abc.ABC):
    """Abstract base class for layout elements"""

    @abc.abstractmethod
    def bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the layout element"""
        pass

    @abc.abstractmethod
    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
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
        """Return the descendants of the layout element"""
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
        """Return `true` if the layout element is equal to another layout element, `false` otherwise"""
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
        """Return `true` if another layout element is a descendant of the layout element, `false` otherwise"""
        return other in self.descendants()

    def to_shapely(self, to_polygons: bool = False) -> shapely.GeometryCollection:
        """Return a shapely collection of geometries reproducing the drawing elements of the layout element"""
        geom_collection = []
        for drawing_element in self.drawing_elements():
            geom_collection += drawing_element.to_shapely(to_polygons=to_polygons).geoms
        return shapely.GeometryCollection(geom_collection)

    def anchor_point(self, anchor_name: str) -> momapy.geometry.Point:
        """Return an anchor point of the layout element"""
        return getattr(self, anchor_name)()
