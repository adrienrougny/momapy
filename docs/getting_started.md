# Getting started

## Installation

momapy is available as a Python package and can be installed with pip as follows:

`pip install momapy`

## Usage

Typical usage of momapy includes reading a map and exploring its model:

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

render_map(map_, "my_file.pdf", format="pdf", renderer="skia")
```

## User manual

A user manual showcasing the main feature of momapy is available here: [User manual](demo.ipynb).

## Documentation

A complete documentaton is available here: [API reference](api_reference/momapy.md).
