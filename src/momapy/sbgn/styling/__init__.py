import pathlib
import os

import momapy.styling

current_dir = os.getcwd()
os.chdir(pathlib.Path(__file__).parent)

cs_default = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("cs_default.css")
)
"""Default colorscheme style sheet"""
cs_black_and_white = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("cs_black_and_white.css")
)
"""Black and white colorscheme style sheet"""
sbgned = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("sbgned.css")
)
"""SBGN-ED style sheet"""
newt = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("newt.css")
)
"""Newt style sheet"""
fs_shadows = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("fs_shadows.css")
)
"""Shadows style sheet"""
os.chdir(current_dir)  # ugly, to fix later
