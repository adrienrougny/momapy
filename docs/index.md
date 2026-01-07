# <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span>

<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> is a library for working with molecular maps.
It currently supports [SBGN](https://www.sbgn.org) and [CellDesigner](https://www.celldesigner.org/) maps.
Its key feature is its definition of a map, that is formed of two entities: a model, that describes what concepts are represented, and a layout, that describes how these concepts are represented.
This definition is borrowed from [SBML](https://www.sbml.org) and its extensions layout+render, that allow users to add a layout to an SBML model.
<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> aims at extending this definition to SBGN and CellDesigner maps.

Features of <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span>:

![Image title](features.png)

## Installation

<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> is available as a Python package and can be installed with pip as follows (Python >=3.10,<=3.12):

`pip install momapy`

### Optional dependencies

<span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> includes several optional dependencies for rendering maps with the skia or cairo backends:

**skia**

`pip install momapy[skia]`

This extra depends on skia-python (<https://github.com/kyamagu/skia-python>), which itself depends on the following system packages:

* opengl
* libegl
* fontconfig

**cairo**

`pip install momapy[cairo]`

This extra depends on pygobject (<https://pygobject.gnome.org/guide/sysdeps.html>), which itself depends on the following system packages:

* glib
* libffi

**all**

All optional dependencies can also be installed together:

`pip install momapy[all]`

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

## User manual

A user manual showcasing the main feature of <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span> is available here: [User manual](demo.ipynb).

## Documentation

A complete documentaton for <span style="font-weight:bold;color:rgb(22 66 81)">moma</span><span style="font-weight:bold;color:rgb(242 200 100)">py</span>'s API is available here: [API reference](api_reference/momapy.md).
