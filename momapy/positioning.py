from typing import Union, Optional, Collection

import momapy.core
import momapy.geometry
import momapy.builder
import momapy.drawing


def right_of(obj, distance):
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.east()
    else:
        raise TypeError
    return source_point + (distance, 0)


def left_of(obj, distance):
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.west()
    else:
        raise TypeError
    return source_point - (distance, 0)


def above_of(obj, distance):
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.north()
    else:
        raise TypeError
    return source_point - (0, distance)


def below_of(obj, distance):
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.south()
    else:
        raise TypeError
    return source_point + (0, distance)


def above_left_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.north_west()
    else:
        raise TypeError
    return source_point - (distance2, distance1)


def above_right_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.north_east()
    else:
        raise TypeError
    return source_point + (distance2, -distance1)


def below_left_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.south_west()
    else:
        raise TypeError
    return source_point + (-distance2, distance1)


def below_right_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, momapy.geometry.Point):
        source_point = obj
    elif isinstance(obj, momapy.core.NodeLayoutElement):
        source_point = obj.south_east()
    else:
        raise TypeError
    return source_point + (distance2, distance1)


def fit(
    elements: Collection[
        momapy.core.LayoutElement,
        momapy.geometry.Bbox,
        momapy.geometry.Point,
        momapy.builder.LayoutElementBuilder,
        momapy.builder.BboxBuilder,
        momapy.builder.PointBuilder,
    ],
    xsep: float = 0,
    ysep: float = 0,
):
    if len(elements) == 0:
        raise ValueError("elements must contain at least one element")
    points = []
    for element in elements:
        if isinstance(
            element, (momapy.geometry.Point, momapy.builder.PointBuilder)
        ):
            points.append(element)
        elif isinstance(
            element, (momapy.geometry.Bbox, momapy.builder.BboxBuilder)
        ):
            points.append(element.north_west())
            points.append(element.south_east())
        elif isinstance(
            element,
            (momapy.core.LayoutElement, momapy.builder.LayoutElementBuilder),
        ):
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
    return (
        momapy.geometry.Point(min_x + width / 2, min_y + height / 2),
        width,
        height,
    )


def fraction_of(
    arc_layout_element: momapy.core.ArcLayoutElement, fraction: float
):
    current_length = 0
    length_to_reach = fraction * arc_layout_element.length()
    for segment in arc_layout_element.segments():
        current_length += segment.length()
        if current_length >= length_to_reach:
            break
    position, angle = momapy.geometry.get_position_and_angle_at_fraction(
        segment, fraction
    )
    transform = tuple([momapy.geometry.Rotation(angle, position)])
    return position, transform


def set_fraction_of(
    obj: Union[
        momapy.builder.NodeLayoutElementBuilder, momapy.builder.BboxBuilder
    ],
    arc_layout_element: Union[
        momapy.core.ArcLayoutElement, momapy.builder.ArcLayoutElementBuilder
    ],
    fraction: float,
    anchor: Optional[str] = None,
):
    position, transform = fraction_of(arc_layout_element, fraction)
    set_position(obj, position, anchor)
    obj.transform = transform


def set_position(
    obj: Union[
        momapy.builder.NodeLayoutElementBuilder, momapy.builder.BboxBuilder
    ],
    position: momapy.geometry.Point,
    anchor: Optional[str] = None,
):
    obj.position = position
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += obj.position - p


def set_right_of(
    obj1: Union[
        momapy.builder.NodeLayoutElementBuilder, momapy.builder.BboxBuilder
    ],
    obj2,
    distance,
    anchor=None,
):
    position = right_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_fit(
    obj: Union[
        momapy.builder.NodeLayoutElementBuilder, momapy.builder.BboxBuilder
    ],
    elements,
    xsep=0,
    ysep=0,
):
    obj.position, obj.width, obj.height = fit(elements, xsep, ysep)
