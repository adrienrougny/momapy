"""CellDesigner layout-building helpers and constants.

Functions and constants for constructing momapy layout objects from
CellDesigner XML data.
"""

import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.celldesigner.core
import momapy.celldesigner.io.celldesigner._parsing

_DEFAULT_FONT_FAMILY = momapy.drawing.DEFAULT_FONT_FAMILY
_DEFAULT_FONT_SIZE = 12.0
_DEFAULT_MODIFICATION_FONT_SIZE = 9.0
_DEFAULT_FONT_FILL = momapy.coloring.black


def make_empty_layout(cd_element):
    layout = momapy.celldesigner.core.CellDesignerLayoutBuilder()
    return layout


def set_layout_size_and_position(cd_model, layout):
    _parsing = momapy.celldesigner.io.celldesigner._parsing
    layout.width = float(_parsing.get_width(cd_model))
    layout.height = float(_parsing.get_height(cd_model))
    layout.position = momapy.geometry.Point(layout.width / 2, layout.height / 2)


def make_segments(points):
    segments = []
    for current_point, following_point in zip(points[:-1], points[1:]):
        segment = momapy.geometry.Segment(current_point, following_point)
        segments.append(segment)
    return segments


def make_points(cd_edit_points):
    if getattr(cd_edit_points, "text", None) is not None:
        cd_edit_points = cd_edit_points.text
    cd_coordinates = [
        cd_edit_point.split(",") for cd_edit_point in cd_edit_points.split(" ")
    ]
    points = [
        momapy.geometry.Point(float(cd_coordinate[0]), float(cd_coordinate[1]))
        for cd_coordinate in cd_coordinates
    ]
    return points
