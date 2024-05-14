cp ../src/momapy/celldesigner/io/__init__.py __init__.py.save
xsdata ../schemas/celldesigner/CellDesigner.xsd --debug --structure-style single-package --package _celldesigner_parser
mv __init__.py.save ../src/momapy/celldesigner/io/__init__.py
rm __init__.py
mv celldesigner_parser.py ../src/momapy/celldesigner/io/_celldesigner_parser.py
