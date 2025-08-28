# momapy

`MomaPy` is a new Python library for working with molecular maps such as SBGN maps.
Its key feature is its definition of a map, that is now formed of two entities: a model, that describes what concepts are represented, and a layout, that describes how these concepts are represented.
This definition is borrowed from SBML and its layout/render extensions, that allow users to add a layout to an SBML model.
`MomaPy` aims at extending this definition to all types of molecular maps, and in particular to SBGN maps.

`MomaPy` offers the following features:

* support for SBGN PD and AF maps (read/write SBGN-ML with annotations, rendering information, and notes) and CellDesigner (read only, with annotations)
* decomposition of a map object into:
  * a model object;
  * a layout object;
  * a mapping between the model and layout objects' subelements.
* map, model, layout and mapping objects comparison; fast object in set checking
* rendering of maps to images (SVG, PDF, JPEG, PNG, WebP) and other surfaces (e.g. GLFW window)
* support for styling and css like stylesheets (including effects such as shadows)
* automatic geometry and anchors (for arcs, shape borders)
* local positioning (e.g. right of shape, fit set of shapes)
* easy extension with new model and layout subelements

The documentation for `momapy` is available [here](https://adrienrougny.github.io/momapy/).
