from typing import Union, Optional

from momapy.core import LayoutElement, NodeLayoutElement, LayoutElementReference
from momapy.geometry import Point, Bbox
from momapy.builder import LayoutElementBuilder, PointBuilder, BboxBuilder, NodeLayoutElementBuilder
from momapy.drawing import translate, rotate

def right_of(obj, distance):
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.east()
    else:
        raise TypeError
    return source_point + (distance, 0)

def left_of(obj, distance):
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.west()
    else:
        raise TypeError
    return source_point - (distance, 0)

def above_of(obj, distance):
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.north()
    else:
        raise TypeError
    return source_point + (0, distance)

def below_of(obj, distance):
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.south()
    else:
        raise TypeError
    return source_point - (0, distance)

def above_left_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.north_west()
    else:
        raise TypeError
    return source_point + (-distance2, distance1)

def above_right_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.north_east()
    else:
        raise TypeError
    return source_point + (distance2, distance1)

def below_left_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.south_west()
    else:
        raise TypeError
    return source_point - (distance2, distance1)

def below_right_of(obj, distance1, distance2=None):
    if distance2 is None:
        distance2 = distance1
    if isinstance(obj, Point):
        source_point = obj
    elif isinstance(obj, NodeLayoutElement):
        source_point = obj.south_east()
    else:
        raise TypeError
    return source_point + (distance2, -distance1)

def fit(elements, xsep=0, ysep=0):
    if len(elements) == 0:
        raise ValueError("elements must contain at least one element")
    points = []
    for element in elements:
        if isinstance(element, (Point, PointBuilder)):
            points.append(element)
        elif isinstance(element, (Bbox, BboxBuilder)):
            points.append(element.north_west())
            points.append(element.south_east())
        elif isinstance(element, (LayoutElement, LayoutElementBuilder)):
            bbox = element.bbox()
            points.append(bbox.north_west())
            points.append(bbox.south_east())
        elif isinstance(element, LayoutElementReference):
            pass
        else:
            raise TypeError
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
    return Bbox(Point(min_x + width / 2, min_y + height / 2), width, height)

def fraction_of(arc_layout_element, fraction):
    position, angle = arc_layout_element.fraction(fraction)
    transform = tuple([translate(position.x, position.y),
                       rotate(angle), translate(-position.x, -position.y)])
    return position, transform

def set_position_at(obj: Union[NodeLayoutElementBuilder, BboxBuilder], position: Point, anchor: Optional[str]=None) -> None:
    obj.position = position
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += (obj.position - p)

def set_position_at_right_of(obj1: Union[NodeLayoutElementBuilder, BboxBuilder], obj2, distance, anchor=None):
    obj1.position = right_of(obj2, distance)
    if anchor is not None:
        p = getattr(obj1, anchor)()
        obj1.position += (obj1.position - p)

def set_position_at_fraction_of(obj, arc_layout_element, fraction, anchor=None):
    position, transform = fraction_of(arc_layout_element, fraction)
    obj.position, obj.transform = position, transform
    if anchor is not None:
        p = getattr(obj, anchor)()
        obj.position += (obj.position - p)
