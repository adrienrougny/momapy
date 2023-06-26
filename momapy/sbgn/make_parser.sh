cp __init__.py __init__.py.save
xsdata schema/sbgn-ml.xsd --debug --structure-style single-package --package parser
mv __init__.py.save __init__.py
