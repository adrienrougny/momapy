"""Styling module for SBGN maps.

This subpackage bundles SBGN stylesheets as `.css` data files alongside
Python `StyleSheet` objects that load them. The CSS files live next to
this module so that relative `@import` directives inside them resolve
correctly.

Exposed stylesheets (loaded from the sibling `.css` files):

- `cs_default` — default colorscheme (`cs_default.css`)
- `cs_black_and_white` — black-and-white colorscheme (`cs_black_and_white.css`)
- `sbgned` — SBGN-ED look (`sbgned.css`)
- `newt` — Newt look (`newt.css`)
- `fs_shadows` — drop-shadow font style (`fs_shadows.css`)

Additional `.css` files in this directory (e.g. `default.css`,
`default_colorscheme.css`, `white_colorscheme.css`, `shadows.css`,
`sbgned_no_cs.css`, `newt_no_cs.css`) are included as `@import` targets
of the stylesheets above and are not exposed as Python attributes.
"""

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
newt = momapy.styling.StyleSheet.from_file(pathlib.Path(__file__).with_name("newt.css"))
"""Newt style sheet"""
fs_shadows = momapy.styling.StyleSheet.from_file(
    pathlib.Path(__file__).with_name("fs_shadows.css")
)
"""Shadows style sheet"""
os.chdir(current_dir)  # ugly, to fix later
