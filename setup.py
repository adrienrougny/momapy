from distutils.core import setup

setup(
    name="momapy",
    version="1.0",
    description="Molecular Maps Python library",
    author="Adrien Rougny",
    author_email="adrienrougny@gmail.com",
    packages=["momapy", "momapy.sbgn", "momapy.sbgn.styling"],
    install_requires=[
        "libsbgnpy",
        "frozendict",
        "pycairo",
        "pygobject",
        "numpy",
        "pyparsing",
        "skia-python",
    ],
    package_data={"": ["*.css"]},
    include_package_data=True,
)
