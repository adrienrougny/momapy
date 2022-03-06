from distutils.core import setup

setup(name = "momapy",
    version = "1.0",
    description = 'Molecular Maps Python library',
    author = "Adrien Rougny",
    author_email = "adrienrougny@gmail.com",
    packages = ["momapy"],
    install_requires = [
        "libsbgnpy",
    ],
)
