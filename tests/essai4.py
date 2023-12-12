import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

WIDTH = 500
HEIGHT = 500
REC_WIDTH = 8
REC_HEIGHT = 8
VERTICAL_SEP = 2
HORIZONTAL_SEP = 2

class DA(Gtk.DrawingArea):

    def __init__(self, **properties):
        super().__init__(**properties)
        self.x = 0
        self.y = 0
        self.connect('draw', self.draw)
        self.set_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        self.connect("motion_notify_event", self.tick)

    def draw(self, widget, ctx):
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(0.1)

        for j in range(HEIGHT // (REC_HEIGHT + VERTICAL_SEP))[1:]:
            for i in range(WIDTH // (REC_WIDTH + HORIZONTAL_SEP)):
                ctx.rectangle(
                        i * (REC_WIDTH + HORIZONTAL_SEP),
                        j * (REC_HEIGHT + VERTICAL_SEP),
                        REC_WIDTH,
                        REC_HEIGHT)
                ctx.stroke()
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(1)
        ctx.rectangle(
                self.x,
                self.y,
                REC_WIDTH,
                REC_HEIGHT)
        ctx.stroke()

    def tick(self, widget, event):
        self.x = event.x
        self.y = event.y
        self.queue_draw()
        return True

if __name__ == '__main__':
    win = Gtk.Window()
    win.connect('destroy', lambda w: Gtk.main_quit())
    win.set_default_size(WIDTH, HEIGHT)
    da = DA()
    win.add(da)
    win.show_all()
    Gtk.main()
