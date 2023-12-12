cp __init__.py __init__.py.save
xsdata schema/CellDesigner.xsd --structure-style single-package --package parser
mv __init__.py.save __init__.py
