"""Functions for positioning layout elements and related objects relatively to other objects"""

import collections.abc

import momapy.core
import momapy.geometry
import momapy.builder


def right_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Compute and return the point right of the given object at a given distance"""
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.east()
    else:
        raise TypeError
    return source_point + (distance, 0)


def left_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Compute and return the point left of the given object at a given distance"""
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.west()
    else:
        raise TypeError
    return source_point - (distance, 0)


def above_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Compute and return the point above of the given object at a given distance"""
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.north()
    else:
        raise TypeError
    return source_point - (0, distance)


def below_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Compute and return the point below of the given object at a given distance"""
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.south()
    else:
        raise TypeError
    return source_point + (0, distance)


def above_left_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Compute and return the point above left of the given object at a given distance"""
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.north_west()
    else:
        raise TypeError
    return source_point - (distance2, distance1)


def above_right_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Compute and return the point above right of the given object at a given distance"""
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.north_east()
    else:
        raise TypeError
    return source_point + (distance2, -distance1)


def below_left_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Compute and return the point below left of the given object at a given distance"""
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.south_west()
    else:
        raise TypeError
    return source_point + (-distance2, distance1)


def below_right_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Compute and return the point below right of the given object at a given distance"""
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.Node):
        source_point = obj.south_east()
    else:
        raise TypeError
    return source_point + (distance2, distance1)


def fit(
    elements: collections.abc.Collection[
        momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.geometry.Point
        | momapy.geometry.PointBuilder
    ],
    xsep: float = 0,
    ysep: float = 0,
) -> momapy.geometry.Bbox:
    """Compute and return the bounding box fitting a collection of objects, with given margins"""
    if not elements:
        raise ValueError("elements must contain at least one element")
    points = []
    for element in elements:
        if momapy.builder.isinstance_or_builder(element, momapy.geometry.Point):
            points.append(element)
        elif momapy.builder.isinstance_or_builder(element, momapy.geometry.Bbox):
            points.append(element.north_west())
            points.append(element.south_east())
        elif momapy.builder.isinstance_or_builder(element, momapy.core.LayoutElement):
            bbox = element.bbox()
            points.append(bbox.north_west())
            points.append(bbox.south_east())
        else:
            raise TypeError(f"{type(element)} not supported")
    point = points[0]
    max_x = point.x
    max_y = point.y
    min_x = point.x
    min_y = point.y
    for point in points[1:]:
        if point.x > max_x:
            max_x = point.x
        elif point.x < min_x:
            min_x = point.x
        if point.y > max_y:
            max_y = point.y
        elif point.y < min_y:
            min_y = point.y
    max_x += xsep
    min_x -= xsep
    max_y += ysep
    min_y -= ysep
    width = max_x - min_x
    height = max_y - min_y
    bbox = momapy.geometry.Bbox(
        momapy.geometry.Point(min_x + width / 2, min_y + height / 2),
        width,
        height,
    )
    return bbox


def mid_of(
    obj1: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
):
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj2 = obj2.center()
    segment = momapy.geometry.Segment(obj1, obj2)
    return segment.get_position_at_fraction(0.5)


def cross_vh_of(
    obj1: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
):
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj2 = obj2.center()
    x = obj1.x
    y = obj2.y
    return momapy.geometry.Point(x, y)


def cross_hv_of(
    obj1: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
):
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.Node)
    ):
        obj2 = obj2.center()
    y = obj1.y
    x = obj2.x
    return momapy.geometry.Point(x, y)


def fraction_of(
    arc_layout_element: (momapy.core.SingleHeadedArc | momapy.core.DoubleHeadedArc),
    fraction: float,
) -> tuple[momapy.geometry.Point, float]:
    """Return the position on an arc at a given fraction and the angle formed of the tangant of the arc at that position and the horizontal"""
    position, angle = arc_layout_element.fraction(fraction)
    return position, angle


def set_position(
    obj: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    position: momapy.geometry.Point | momapy.geometry.PointBuilder,
    anchor: str | None = None,
):
    """Set the position of a given builder object"""
    obj.position = position
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += obj.position - p


def set_right_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set the position of a given builder object right of another given object at a given distance"""
    position = right_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_left_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set the position of a given builder object left of another given object at a given distance"""
    position = left_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set the position of a given builder object above of another given object at a given distance"""
    position = above_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_below_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set the position of a given builder object below of another given object at a given distance"""
    position = below_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_left_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set the position of a given builder object above left of another given object at a given distance"""
    position = above_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_above_right_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set the position of a given builder object above right of another given object at a given distance"""
    position = above_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_left_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set the position of a given builder object below left of another given object at a given distance"""
    position = below_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_right_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set the position of a given builder object below right of another given object at a given distance"""
    position = below_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_fit(
    obj: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    elements: collections.abc.Collection[
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.LayoutElement
        | momapy.core.LayoutElementBuilder
    ],
    xsep: float = 0,
    ysep: float = 0,
    anchor: str | None = None,
):
    """Set the position, width and height of a given builder object to fit a given collection of other objects"""
    bbox = fit(elements, xsep, ysep)
    obj.width = bbox.width
    obj.height = bbox.height
    set_position(obj, bbox.position, anchor)


def set_fraction_of(
    obj: momapy.core.NodeBuilder,
    arc_layout_element: (momapy.core.SingleHeadedArc | momapy.core.DoubleHeadedArc),
    fraction: float,
    anchor: str | None = None,
):
    """Set the position and rotation of a given builder object to lay at a given fraction of a given arc"""
    position, angle = fraction_of(arc_layout_element, fraction)
    rotation = momapy.geometry.Rotation(angle, position)
    set_position(obj, position, anchor)
    obj.transform = momapy.core.TupleBuilder([rotation])


def set_mid_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    anchor: str | None = None,
):
    position = mid_of(obj2, obj3)
    set_position(obj1, position, anchor)


def set_cross_hv_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    anchor: str | None = None,
):
    position = cross_hv_of(obj2, obj3)
    set_position(obj1, position, anchor)


def set_cross_vh_of(
    obj1: momapy.core.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.Node
        | momapy.core.NodeBuilder
    ),
    anchor: str | None = None,
):
    position = cross_vh_of(obj2, obj3)
    set_position(obj1, position, anchor)
