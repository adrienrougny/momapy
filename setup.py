import os
from distutils.core import setup

os.system("echo 'Setting BEZIER_NO_EXTENSION=True'")
os.system("export BEZIER_NO_EXTENSION=True")

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
        "momapy.sbgn.io",
        "momapy.celldesigner",
        "momapy.sbml",
        "momapy.rendering",
        "momapy.demo",
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
        "shapely~=2.0rc1",
        "ipykernel",
        "pyparsing",
    ],
    package_data={"": ["*.css"]},
    include_package_data=True,
)
