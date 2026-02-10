"""Animation creation module for generating video files from layouts.

This module provides tools for creating animations by rendering layout frames
and compiling them into video files using ffmpeg.

Example:
    >>> from momapy.animating import Animator
    >>> from momapy.core import Layout
    >>> layout = Layout(...)
    >>> animator = Animator(layout, fps=30)
    >>> animator.frames(60)  # Hold for 60 frames
    >>> animator.build("output.mp4")
"""

from dataclasses import dataclass
import tempfile
import ffmpeg

import momapy.core
import momapy.rendering


@dataclass
class Animator(object):
    """Animator for creating video animations from layouts.

    This class manages the creation of video animations by collecting frames
    rendered from a layout and compiling them using ffmpeg.

    Attributes:
        layout: The layout to animate.
        fps: Frames per second for the output video.

    Example:
        >>> animator = Animator(my_layout, fps=60)
        >>> animator.frames(30)  # 0.5 seconds at 60 fps
        >>> animator.mseconds(1000)  # 1 second
        >>> animator.build("animation.mp4")
    """

    layout: momapy.core.Layout
    fps: int = 60

    def __post_init__(self):
        self._initialize()

    def _initialize(self):
        flimages = tempfile.mkstemp()
        self._flimages = (open(flimages[1], "w"), flimages[1])
        self._n_images = 0

    def frames(self, n_frames: int):
        """Add a specified number of frames to the animation.

        Renders the current layout and adds it to the animation for the
        specified number of frames.

        Args:
            n_frames: Number of frames to add.

        Example:
            >>> animator.frames(60)  # Add 1 second at 60 fps
        """
        fimage = tempfile.mkstemp()
        self._n_images += 1
        momapy.rendering.render_layout(self.layout, fimage[1], format_="png")
        for i in range(n_frames):
            self._flimages[0].write(f"file '{fimage[1]}\n")

    def mseconds(self, n_mseconds: float):
        """Add frames for a specified duration in milliseconds.

        Converts milliseconds to frames based on the fps setting and adds
        the corresponding number of frames.

        Args:
            n_mseconds: Duration in milliseconds.

        Example:
            >>> animator.mseconds(1000)  # Add 1 second of animation
            >>> animator.mseconds(500)   # Add 0.5 seconds of animation
        """
        n_frames = round(n_mseconds / 1000 * self.fps)
        self.frames(n_frames)

    def build(self, output_file, vcodec="libx264"):
        """Build the video file from collected frames.

        Compiles all frames into a video file using ffmpeg.

        Args:
            output_file: Path to the output video file.
            vcodec: Video codec to use (default: libx264).

        Example:
            >>> animator.build("output.mp4")
            >>> animator.build("output.mp4", vcodec="libx265")
        """
        self._flimages[0].close()
        ffmpeg.input(self._flimages[1], r=str(self.fps), f="concat", safe="0").output(
            output_file, vcodec=vcodec
        ).run(quiet=True, overwrite_output=True)
