import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from momapy.sbgn.io import read_file
from momapy.renderer import GTKRenderer
from momapy.geometry import Point, relative
from momapy.shapes import Rectangle
from momapy.arcs import Arrow
from momapy.types import NodeLayoutElement, get_or_make_builder_cls
from momapy.color import rgba


class MyRenderer(GTKRenderer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        self.drawing_area.connect("button-press-event", self.on_click)
        self.drawing_area.connect("motion_notify_event", self.on_motion)
        self.moving_layout_element = None

    def on_draw(self, widget, context):
        self.set_context(context)
        self.render_map(self.map)

    def on_click(self, widget, event):
        if self.moving_layout_element is not None:
            self.moving_layout_element = None
            window.get_window().set_cursor(None)
        else:
            for layout_element in self.map.layout.elements:
                if isinstance(layout_element, get_or_make_builder_cls(NodeLayoutElement)):
                    if self.mouse_in_node_layout_element(layout_element, event.x, event.y):
                        self.moving_layout_element = layout_element
                        watch_cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
                        window.get_window().set_cursor(watch_cursor)

    def on_motion(self, widget, event):
        if self.moving_layout_element is not None:
            self.moving_layout_element.position = Point(event.x, self.cairo_renderer._transform_y_coord(event.y))
            if self.moving_layout_element.label is not None:
                self.moving_layout_element.label.position = Point(event.x, self.cairo_renderer._transform_y_coord(event.y))
            self.drawing_area.queue_draw()
        return True

    def mouse_in_node_layout_element(self, node_layout_element, x, y):
        bbox = node_layout_element.bbox
        y = self.cairo_renderer._transform_y_coord(y)
        if x >= bbox.west.x and x <= bbox.east.x and y >= bbox.south.y and y <= bbox.north.y:
            return True
        return False


map_ = read_file("essai.sbgn", return_builder=True)
for entity_pool in map_.model.entity_pools:
    if entity_pool.label == "ABC":
        layout_element = next(iter(map_.model_layout_mapping[entity_pool]))
        break
new_layout_element = map_.new_layout_element(Rectangle, position=relative(layout_element, "north"), width=20, height=10, order=1, fill=rgba(255, 255, 255, 1))
map_.add_layout_element(new_layout_element)
abc = layout_element
for entity_pool in map_.model.entity_pools:
    if entity_pool.label == "GHI":
        layout_element = next(iter(map_.model_layout_mapping[entity_pool]))
        break
ghi = layout_element
new_arc = Arrow(source=abc, target=ghi, points=(relative(abc, "border", (relative(ghi, "center"),)), relative(ghi, "border", (relative(abc, "center"),))), order=2, width=15, height=15, fill=rgba(0, 0, 0, 1))
map_.add_layout_element(new_arc)

window = Gtk.Window()
window.connect('destroy', lambda w: Gtk.main_quit())
window.set_default_size(map_.layout.width, map_.layout.height)
drawing_area = Gtk.DrawingArea()
window.add(drawing_area)
renderer = MyRenderer(drawing_area=drawing_area, width=map_.layout.width, height=map_.layout.height)
renderer.map = map_
window.show_all()
Gtk.main()
