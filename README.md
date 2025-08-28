# <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span>

<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> is a library for working with molecular maps.
It currently supports [SBGN](https://www.sbgn.org) and [CellDesigner](https://www.celldesigner.org/) maps.
Its key feature is its definition of a map, that is formed of two entities: a model, that describes what concepts are represented, and a layout, that describes how these concepts are represented.
This definition is borrowed from [SBML](https://www.sbml.org) and its extensions layout+render, that allow users to add a layout to an SBML model.
<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> aims at extending this definition to SBGN and CellDesigner maps.

Features of <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> include the following:

* support for SBGN PD and AF maps (read/write SBGN-ML with annotations, rendering information, and notes) and CellDesigner (read only, with annotations)
* decomposition of a map object into:
  * a model object;
  * a layout object;
  * a mapping from layout element objects to model element objects.
* map, model, layout and mapping objects comparison; fast object in set checking
* rendering of maps to images (SVG, PDF, JPEG, PNG, WebP) and other surfaces (e.g. GLFW window)
* support for styling and CSS like stylesheets (including effects such as shadows)
* automatic geometry and anchors (for arcs, shape borders)
* local positioning (e.g. right of shape, fit set of shapes)
* easy extension with new model and layout element types

## Installation

<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> is available as a Python package and can be installed with pip as follows:

`pip install momapy`

## Usage

Typical usage of <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> includes reading a map and exploring its model:

```python
import momapy.sbgn.io.sbgnml
from momapy.io import read

map_ = read("my_map.sbgn").obj
for process in map_.model.processes:
    print(process)
```

Or rendering its layout:

```python
import momapy.rendering.skia
from momapy.rendering.core import render_map

render_map(map_, "my_file.pdf", format_="pdf", renderer="skia")
```

## Documentation

The documentation for <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> can be found [here](https://adrienrougny.github.io/momapy/).
