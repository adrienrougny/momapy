from typing import Union, Optional, Collection

import momapy.core
import momapy.geometry
import momapy.builder
import momapy.drawing


def right_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
):
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.east()
    else:
        raise TypeError
    return source_point + (distance, 0)


def left_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
):
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.west()
    else:
        raise TypeError
    return source_point - (distance, 0)


def above_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
):
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.north()
    else:
        raise TypeError
    return source_point - (0, distance)


def below_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
):
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.south()
    else:
        raise TypeError
    return source_point + (0, distance)


def above_left_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
):
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.north_west()
    else:
        raise TypeError
    return source_point - (distance2, distance1)


def above_right_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
):
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.north_east()
    else:
        raise TypeError
    return source_point + (distance2, -distance1)


def below_left_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
):
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.south_west()
    else:
        raise TypeError
    return source_point + (-distance2, distance1)


def below_right_of(
    obj: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
):
    if distance2 is None:
        distance2 = distance1
    if momapy.builder.isinstance_or_builder(obj, momapy.geometry.Point):
        source_point = obj
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.NodeLayout):
        source_point = obj.south_east()
    else:
        raise TypeError
    return source_point + (distance2, distance1)


def fit(
    elements: Collection[
        Union[
            momapy.core.LayoutElement,
            momapy.core.LayoutElementBuilder,
            momapy.geometry.Bbox,
            momapy.geometry.BboxBuilder,
            momapy.geometry.Point,
            momapy.geometry.PointBuilder,
        ]
    ],
    xsep: float = 0,
    ysep: float = 0,
):
    if len(elements) == 0:
        raise ValueError("elements must contain at least one element")
    points = []
    for element in elements:
        if momapy.builder.isinstance_or_builder(element, momapy.geometry.Point):
            points.append(element)
        elif momapy.builder.isinstance_or_builder(
            element, momapy.geometry.Bbox
        ):
            points.append(element.north_west())
            points.append(element.south_east())
        elif momapy.builder.isinstance_or_builder(
            element, momapy.core.LayoutElement
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
    arc_layout_element: Union[
        momapy.core.ArcLayout, momapy.core.ArcLayoutBuilder
    ],
    fraction: float,
):
    position, angle = arc_layout_element.fraction(fraction)
    transform = tuple([momapy.geometry.Rotation(angle, position)])
    return position, transform


def set_position(
    obj: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    position: Union[momapy.geometry.Point, momapy.geometry.PointBuilder],
    anchor: Optional[str] = None,
):
    obj.position = position
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += obj.position - p


def set_right_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
    anchor=None,
):
    position = right_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_left_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
    anchor=None,
):
    position = left_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
    anchor=None,
):
    position = above_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_below_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance: float,
    anchor=None,
):
    position = below_of(obj2, distance)
    set_position(obj1, position, anchor)


def set_above_left_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
    anchor=None,
):
    position = above_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_above_right_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
    anchor=None,
):
    position = above_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_left_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
    anchor=None,
):
    position = below_left_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_below_right_of(
    obj1: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    obj2: Union[
        momapy.geometry.Point,
        momapy.geometry.PointBuilder,
        momapy.geometry.Bbox,
        momapy.geometry.BboxBuilder,
        momapy.core.LayoutElement,
        momapy.core.LayoutElementBuilder,
    ],
    distance1: float,
    distance2: Optional[float] = None,
    anchor=None,
):
    position = below_right_of(obj2, distance1, distance2)
    set_position(obj1, position, anchor)


def set_fit(
    obj: Union[momapy.core.NodeLayoutBuilder, momapy.geometry.BboxBuilder],
    elements: Collection[
        Union[
            momapy.geometry.Point,
            momapy.geometry.PointBuilder,
            momapy.geometry.Bbox,
            momapy.geometry.BboxBuilder,
            momapy.core.LayoutElement,
            momapy.core.LayoutElementBuilder,
        ]
    ],
    xsep: float = 0,
    ysep: float = 0,
    anchor: Optional[str] = None,
):
    position, obj.width, obj.height = fit(elements, xsep, ysep)
    set_position(obj, position, anchor)


def set_fraction_of(
    obj: momapy.core.NodeLayoutBuilder,
    arc_layout_element: Union[
        momapy.core.ArcLayout, momapy.core.ArcLayoutBuilder
    ],
    fraction: float,
    anchor: Optional[str] = None,
):
    position, transform = fraction_of(arc_layout_element, fraction)
    set_position(obj, position, anchor)
    obj.transform = transform
