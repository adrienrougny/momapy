import pathlib
import os

import momapy.styling

current_dir = os.getcwd()
os.chdir(pathlib.Path(__file__).parent)

default = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./default.css")
)
default_colorscheme = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./default_colorscheme.css")
)
white_colorscheme = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./white_colorscheme.css")
)
sbgned = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./sbgned.css")
)
newt = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./newt.css")
)
shadows = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("./shadows.css")
)
os.chdir(current_dir)  # ugly, to fix later
