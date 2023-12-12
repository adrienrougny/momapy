cp __init__.py __init__.py.save
xsdata sbgnml_schemas/sbgn-ml.xsd --debug --structure-style single-package --package _sbgnml_parser
mv __init__.py.save __init__.py
mv sbgnml_parser.py _sbgnml_parser.py
