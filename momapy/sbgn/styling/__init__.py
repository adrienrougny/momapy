import pathlib

import momapy.styling

default = momapy.styling.read_file(
    pathlib.Path(__file__).with_name("./default.css")
)
default_colorscheme = momapy.styling.read_file(
    pathlib.Path(__file__).with_name("./default_colorscheme.css")
)
white_colorscheme = momapy.styling.read_file(
    pathlib.Path(__file__).with_name("./white_colorscheme.css")
)
vanted = momapy.styling.read_file(
    pathlib.Path(__file__).with_name("./vanted.css")
)
newt = momapy.styling.read_file(pathlib.Path(__file__).with_name("./newt.css"))
shadows = momapy.styling.read_file(
    pathlib.Path(__file__).with_name("./shadows.css")
)
