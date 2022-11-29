from distutils.core import setup

setup(
    name="momapy",
    version="1.0",
    description="A modern library for molecular maps",
    author="Adrien Rougny",
    author_email="adrienrougny@gmail.com",
    packages=[
        "momapy",
        "momapy.sbgn",
        "momapy.sbgn.styling",
        "momapy.celldesigner",
        "momapy.sbml",
        "momapy.rendering",
    ],
    install_requires=[
        "libsbgnpy",
        "frozendict",
        "pycairo",
        "pygobject",
        "numpy",
        "pyparsing",
        "skia-python",
        "xsdata[cli, lxml, soap]",
        "bezier",
        "shapely",
    ],
    package_data={"": ["*.css"]},
    include_package_data=True,
)
