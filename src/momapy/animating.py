from dataclasses import dataclass
import tempfile
import ffmpeg

import momapy.core
import momapy.rendering


@dataclass
class Animator(object):
    layout: momapy.core.Layout
    fps: int = 60

    def __post_init__(self):
        self._initialize()

    def _initialize(self):
        flimages = tempfile.mkstemp()
        self._flimages = (open(flimages[1], "w"), flimages[1])
        self._n_images = 0

    def frames(self, n_frames: int):
        fimage = tempfile.mkstemp()
        self._n_images += 1
        momapy.rendering.render_layout(self.layout, fimage[1], format_="png")
        for i in range(n_frames):
            self._flimages[0].write(f"file '{fimage[1]}\n")

    def mseconds(self, n_mseconds: float):
        n_frames = round(n_mseconds / 1000 * self.fps)
        self.frames(n_frames)

    def build(self, output_file, vcodec="libx264"):
        self._flimages[0].close()
        ffmpeg.input(
            self._flimages[1], r=str(self.fps), f="concat", safe="0"
        ).output(output_file, vcodec=vcodec).run(
            quiet=True, overwrite_output=True
        )
