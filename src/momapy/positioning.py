"""Functions for positioning layout elements and related objects relatively to other objects.

This module provides utilities for calculating positions relative to layout elements,
fitting bounding boxes around collections of elements, and setting positions of
builder objects. Functions support Points, Bboxes, Nodes, and their builder variants.

Example:
    >>> from momapy.positioning import right_of, fit
    >>> from momapy.geometry import Point
    >>> point = Point(0, 0)
    >>> new_point = right_of(point, 10)
    >>> print(new_point)
    Point(x=10, y=0)
"""

import collections.abc

import momapy.core
import momapy.core.builders
import momapy.core.elements
import momapy.core.layout
import momapy.geometry
import momapy.builder


def right_of(
    obj: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Return a point to the right of the given object at the specified distance.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the east anchor point.
        distance: The horizontal distance from the object's reference point.

    Returns:
        A new Point located to the right of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(0, 0)
        >>> right_of(point, 10)
        Point(x=10, y=0)
    """
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Return a point to the left of the given object at the specified distance.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the west anchor point.
        distance: The horizontal distance from the object's reference point.

    Returns:
        A new Point located to the left of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(10, 0)
        >>> left_of(point, 5)
        Point(x=5, y=0)
    """
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Return a point above the given object at the specified distance.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the north anchor point.
        distance: The vertical distance from the object's reference point.

    Returns:
        A new Point located above the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(0, 10)
        >>> above_of(point, 5)
        Point(x=0, y=5)
    """
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
) -> momapy.geometry.Point:
    """Return a point below the given object at the specified distance.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the south anchor point.
        distance: The vertical distance from the object's reference point.

    Returns:
        A new Point located below the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(0, 0)
        >>> below_of(point, 10)
        Point(x=0, y=10)
    """
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Return a point above and to the left of the given object.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the north-west anchor point.
        distance1: The vertical distance (northward) from the object.
        distance2: The horizontal distance (westward) from the object.
            If None, defaults to distance1.

    Returns:
        A new Point located above and to the left of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(10, 10)
        >>> above_left_of(point, 5)
        Point(x=5, y=5)
    """
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Return a point above and to the right of the given object.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the north-east anchor point.
        distance1: The vertical distance (northward) from the object.
        distance2: The horizontal distance (eastward) from the object.
            If None, defaults to distance1.

    Returns:
        A new Point located above and to the right of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(0, 10)
        >>> above_right_of(point, 5, 10)
        Point(x=10, y=5)
    """
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Return a point below and to the left of the given object.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the south-west anchor point.
        distance1: The vertical distance (southward) from the object.
        distance2: The horizontal distance (westward) from the object.
            If None, defaults to distance1.

    Returns:
        A new Point located below and to the left of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(10, 0)
        >>> below_left_of(point, 5)
        Point(x=5, y=5)
    """
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
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
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
) -> momapy.geometry.Point:
    """Return a point below and to the right of the given object.

    Args:
        obj: A Point, Bbox, LayoutElement, or their builder variants.
            For Nodes, uses the south-east anchor point.
        distance1: The vertical distance (southward) from the object.
        distance2: The horizontal distance (eastward) from the object.
            If None, defaults to distance1.

    Returns:
        A new Point located below and to the right of the object.

    Raises:
        TypeError: If obj is not a supported type.

    Example:
        >>> point = momapy.geometry.Point(0, 0)
        >>> below_right_of(point, 5, 10)
        Point(x=10, y=5)
    """
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.layout.Node):
        source_point = obj.south_east()
    else:
        raise TypeError
    return source_point + (distance2, distance1)


def fit(
    elements: collections.abc.Collection[
        momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.geometry.Point
        | momapy.geometry.PointBuilder
    ],
    xsep: float = 0,
    ysep: float = 0,
) -> momapy.geometry.Bbox:
    """Compute a bounding box that fits the given elements with optional margins.

    Args:
        elements: A collection of Points, Bboxes, LayoutElements, or their
            builder variants to fit within the bounding box.
        xsep: Horizontal margin to add to both sides of the bounding box.
        ysep: Vertical margin to add to both sides of the bounding box.

    Returns:
        A Bbox that tightly contains all elements plus the specified margins.

    Raises:
        ValueError: If elements is empty.
        TypeError: If an element has an unsupported type.

    Example:
        >>> points = [momapy.geometry.Point(0, 0), momapy.geometry.Point(10, 10)]
        >>> bbox = fit(points, xsep=2, ysep=2)
        >>> print(bbox.position)
        Point(x=5.0, y=5.0)
    """
    if not elements:
        raise ValueError("elements must contain at least one element")
    points = []
    for element in elements:
        if momapy.builder.isinstance_or_builder(element, momapy.geometry.Point):
            points.append(element)
        elif momapy.builder.isinstance_or_builder(element, momapy.geometry.Bbox):
            points.append(element.north_west())
            points.append(element.south_east())
        elif momapy.builder.isinstance_or_builder(element, momapy.core.elements.LayoutElement):
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
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
) -> momapy.geometry.Point:
    """Return the midpoint between two objects.

    Args:
        obj1: First object (Point, Bbox, Node, or builder).
        obj2: Second object (Point, Bbox, Node, or builder).
            For Bboxes and Nodes, uses their center points.

    Returns:
        A Point at the midpoint between the two objects.

    Example:
        >>> p1 = momapy.geometry.Point(0, 0)
        >>> p2 = momapy.geometry.Point(10, 10)
        >>> mid_of(p1, p2)
        Point(x=5.0, y=5.0)
    """
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.layout.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.layout.Node)
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
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
) -> momapy.geometry.Point:
    """Return the point at the vertical cross of obj1 and horizontal cross of obj2.

    Creates a point using obj1's x-coordinate and obj2's y-coordinate.
    Useful for creating elbow connector points.

    Args:
        obj1: Object providing the x-coordinate (Point, Bbox, Node, or builder).
        obj2: Object providing the y-coordinate (Point, Bbox, Node, or builder).
            For Bboxes and Nodes, uses their center points.

    Returns:
        A Point at (obj1.x, obj2.y).

    Example:
        >>> p1 = momapy.geometry.Point(5, 0)
        >>> p2 = momapy.geometry.Point(0, 10)
        >>> cross_vh_of(p1, p2)
        Point(x=5, y=10)
    """
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.layout.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.layout.Node)
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
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
) -> momapy.geometry.Point:
    """Return the point at the horizontal cross of obj1 and vertical cross of obj2.

    Creates a point using obj1's y-coordinate and obj2's x-coordinate.
    Useful for creating elbow connector points.

    Args:
        obj1: Object providing the y-coordinate (Point, Bbox, Node, or builder).
        obj2: Object providing the x-coordinate (Point, Bbox, Node, or builder).
            For Bboxes and Nodes, uses their center points.

    Returns:
        A Point at (obj2.x, obj1.y).

    Example:
        >>> p1 = momapy.geometry.Point(0, 5)
        >>> p2 = momapy.geometry.Point(10, 0)
        >>> cross_hv_of(p1, p2)
        Point(x=10, y=5)
    """
    if momapy.builder.isinstance_or_builder(
        obj1, (momapy.geometry.Bbox, momapy.core.layout.Node)
    ):
        obj1 = obj1.center()
    if momapy.builder.isinstance_or_builder(
        obj2, (momapy.geometry.Bbox, momapy.core.layout.Node)
    ):
        obj2 = obj2.center()
    y = obj1.y
    x = obj2.x
    return momapy.geometry.Point(x, y)


def fraction_of(
    arc_layout_element: (momapy.core.layout.SingleHeadedArc | momapy.core.layout.DoubleHeadedArc),
    fraction: float,
) -> tuple[momapy.geometry.Point, float]:
    """Return the position and angle at a given fraction along an arc.

    Args:
        arc_layout_element: An arc layout element (SingleHeadedArc or DoubleHeadedArc).
        fraction: A value between 0.0 and 1.0 representing the position along the arc.

    Returns:
        A tuple containing:
            - The Point at the specified fraction along the arc.
            - The angle (in radians) of the tangent at that position.

    Example:
        >>> arc = some_single_headed_arc
        >>> pos, angle = fraction_of(arc, 0.5)  # Midpoint of arc
    """
    position, angle = arc_layout_element.fraction(fraction)
    return position, angle


def set_position(
    obj: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    position: momapy.geometry.Point | momapy.geometry.PointBuilder,
    anchor: str | None = None,
):
    """Set the position of a builder object.

    Args:
        obj: The builder object to position (NodeBuilder or BboxBuilder).
        position: The target position as a Point or PointBuilder.
        anchor: Optional anchor name to align with the position.
            If specified, the object is shifted so that its anchor point
            aligns with the given position.

    Example:
        >>> builder = momapy.builder.get_or_make_builder_cls(MyNode)()
        >>> set_position(builder, momapy.geometry.Point(100, 100), anchor="center")
    """
    obj.position = position
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += obj.position - p


def set_right_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set obj1's position to the right of obj2 at the specified distance.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance: The horizontal distance from obj2.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = right_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_left_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set obj1's position to the left of obj2 at the specified distance.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance: The horizontal distance from obj2.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = left_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set obj1's position above obj2 at the specified distance.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance: The vertical distance from obj2.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = above_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_below_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance: float,
    anchor: str | None = None,
):
    """Set obj1's position below obj2 at the specified distance.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance: The vertical distance from obj2.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = below_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_left_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set obj1's position above and to the left of obj2.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance1: The vertical distance from obj2.
        distance2: The horizontal distance from obj2. Defaults to distance1 if None.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = above_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_above_right_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set obj1's position above and to the right of obj2.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance1: The vertical distance from obj2.
        distance2: The horizontal distance from obj2. Defaults to distance1 if None.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = above_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_left_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set obj1's position below and to the left of obj2.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance1: The vertical distance from obj2.
        distance2: The horizontal distance from obj2. Defaults to distance1 if None.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = below_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_right_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ),
    distance1: float,
    distance2: float | None = None,
    anchor: str | None = None,
):
    """Set obj1's position below and to the right of obj2.

    Args:
        obj1: The builder object to position.
        obj2: The reference object to position relative to.
        distance1: The vertical distance from obj2.
        distance2: The horizontal distance from obj2. Defaults to distance1 if None.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = below_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_fit(
    obj: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    elements: collections.abc.Collection[
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.elements.LayoutElement
        | momapy.core.builders.LayoutElementBuilder
    ],
    xsep: float = 0,
    ysep: float = 0,
    anchor: str | None = None,
):
    """Set obj's dimensions and position to fit the given elements.

    Args:
        obj: The builder object to resize and position.
        elements: Collection of elements to fit within obj.
        xsep: Horizontal margin around the fitted elements.
        ysep: Vertical margin around the fitted elements.
        anchor: Optional anchor name on obj to align with the calculated position.
    """
    bbox = fit(elements, xsep, ysep)
    obj.width = bbox.width
    obj.height = bbox.height
    set_position(obj, bbox.position, anchor)


def set_fraction_of(
    obj: momapy.core.builders.NodeBuilder,
    arc_layout_element: (momapy.core.layout.SingleHeadedArc | momapy.core.layout.DoubleHeadedArc),
    fraction: float,
    anchor: str | None = None,
):
    """Set obj's position and rotation along an arc at the given fraction.

    Args:
        obj: The node builder to position and rotate.
        arc_layout_element: The arc to position along.
        fraction: Position along the arc (0.0 to 1.0).
        anchor: Optional anchor name on obj to align with the calculated position.
    """
    position, angle = fraction_of(arc_layout_element, fraction)
    rotation = momapy.geometry.Rotation(angle, position)
    set_position(obj, position, anchor)
    obj.transform = [rotation]


def set_mid_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    anchor: str | None = None,
):
    """Set obj1's position to the midpoint between obj2 and obj3.

    Args:
        obj1: The builder object to position.
        obj2: First reference object.
        obj3: Second reference object.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = mid_of(obj2, obj3)
    set_position(obj1, position, anchor)


def set_cross_hv_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    anchor: str | None = None,
):
    """Set obj1's position at the horizontal-vertical cross of obj2 and obj3.

    Creates a point using obj2's y-coordinate and obj3's x-coordinate.

    Args:
        obj1: The builder object to position.
        obj2: Object providing the y-coordinate.
        obj3: Object providing the x-coordinate.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = cross_hv_of(obj2, obj3)
    set_position(obj1, position, anchor)


def set_cross_vh_of(
    obj1: momapy.core.builders.NodeBuilder | momapy.geometry.BboxBuilder,
    obj2: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    obj3: (
        momapy.geometry.Point
        | momapy.geometry.PointBuilder
        | momapy.geometry.Bbox
        | momapy.geometry.BboxBuilder
        | momapy.core.layout.Node
        | momapy.core.builders.NodeBuilder
    ),
    anchor: str | None = None,
):
    """Set obj1's position at the vertical-horizontal cross of obj2 and obj3.

    Creates a point using obj2's x-coordinate and obj3's y-coordinate.

    Args:
        obj1: The builder object to position.
        obj2: Object providing the x-coordinate.
        obj3: Object providing the y-coordinate.
        anchor: Optional anchor name on obj1 to align with the calculated position.
    """
    position = cross_vh_of(obj2, obj3)
    set_position(obj1, position, anchor)
