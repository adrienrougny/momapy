from dataclasses import dataclass, InitVar
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Collection, Union
import cairo
import gi
import skia

import math

import momapy.drawing
import momapy.styling
import momapy.positioning
import momapy.geometry
import momapy.builder

renderers = {}


def register_renderer(name, renderer_cls):
    renderers[name] = renderer_cls


def render_map(
    map_,
    output_file,
    format_="pdf",
    renderer="cairo",
    style_sheet=None,
    to_top_left=False,
):
    maps = [map_]
    render_maps(maps, output_file, format_, renderer, style_sheet, to_top_left)


def render_maps(
    maps,
    output_file,
    format_="pdf",
    renderer="cairo",
    style_sheet=None,
    to_top_left=False,
    multi_pages=True,
):
    bboxes = [map_.layout.self_bbox() for map_ in maps]
    position, width, height = momapy.positioning.fit(bboxes)
    max_x = position.x + width / 2
    max_y = position.y + height / 2
    if style_sheet is not None or to_top_left:
        new_maps = []
        for map_ in maps:
            if isinstance(map_, momapy.core.Map):
                new_maps.append(momapy.builder.builder_from_object(map_))
            elif isinstance(map_, momapy.core.MapBuilder):
                new_maps.append(deepcopy(map_))
        maps = new_maps
    if style_sheet is not None:
        if (
            not isinstance(style_sheet, Collection)
            or isinstance(style_sheet, str)
            or isinstance(style_sheet, momapy.styling.StyleSheet)
        ):
            style_sheets = [style_sheet]
        else:
            style_sheets = style_sheet
        style_sheets = [
            momapy.styling.read_file(style_sheet)
            if not isinstance(style_sheet, momapy.styling.StyleSheet)
            else style_sheet
            for style_sheet in style_sheets
        ]
        style_sheet = momapy.styling.join_style_sheets(style_sheets)
        for map_ in maps:
            momapy.styling.apply_style_sheet(map_.layout, style_sheet)
    if to_top_left:
        min_x = position.x - width / 2
        min_y = position.y - height / 2
        max_x -= min_x
        max_y -= min_y
        translation = momapy.geometry.Translation(-min_x, -min_y)
        for map_ in maps:
            if map_.layout.transform is None:
                map_.layout.transform = momapy.core.TupleBuilder()
            map_.layout.transform.append(translation)
    renderer = renderers[renderer].from_file(output_file, max_x, max_y, format_)
    renderer.begin_session()
    for i, map_ in enumerate(maps):
        if multi_pages and i > 0:
            renderer.new_page(map_.layout.width, map_.layout.height)
        renderer.render_map(map_)
    renderer.end_session()


@dataclass
class Renderer(ABC):
    default_stroke: ClassVar[
        Union[momapy.coloring.Color, momapy.drawing.NoneValueType]
    ] = (momapy.drawing.NoneValue,)
    default_stroke_width: ClassVar[float] = 1.0
    default_fill: ClassVar[momapy.coloring.Color] = momapy.coloring.black
    default_stroke_dashoffset: ClassVar[float] = 0.0

    @abstractmethod
    def begin_session(self):
        pass

    @abstractmethod
    def end_session(self):
        pass

    @abstractmethod
    def new_page(self, width, height):
        pass

    @abstractmethod
    def render_map(self, map_):
        pass

    @abstractmethod
    def render_layout_element(self, layout_element):
        pass

    @abstractmethod
    def render_drawing_element(self, drawing_element):
        pass
