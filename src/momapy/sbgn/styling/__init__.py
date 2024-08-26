import pathlib
import os

import momapy.styling

current_dir = os.getcwd()
os.chdir(pathlib.Path(__file__).parent)

cs_default = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("cs_default.css")
)
cs_black_and_white = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("cs_black_and_white.css")
)
sbgned = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("sbgned.css")
)
newt = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("newt.css")
)
fs_shadows = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("fs_shadows.css")
)
os.chdir(current_dir)  # ugly, to fix later
