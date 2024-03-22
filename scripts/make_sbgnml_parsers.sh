cp ../src/momapy/sbgn/io/__init__.py __init__.py.save
xsdata ../schemas/sbgnml/0_2/sbgn-ml.xsd --debug --structure-style single-package --package _sbgnml_parser_0_2
xsdata ../schemas/sbgnml/0_3/sbgn-ml.xsd --debug --structure-style single-package --package _sbgnml_parser_0_3
mv __init__.py.save ../src/momapy/sbgn/io/__init__.py
rm __init__.py
mv sbgnml_parser_0_2.py ../src/momapy/sbgn/io/_sbgnml_parser_0_2.py
mv sbgnml_parser_0_3.py ../src/momapy/sbgn/io/_sbgnml_parser_0_3.py
