"""Library for working with molecular maps programmatically.

This package provides tools for reading, writing, manipulating, and rendering
molecular maps, with support for various formats including SBGN-ML and CellDesigner.

Examples:
    ```python
    from momapy.io.core import read
    from momapy.rendering.core import render_map

    # Read a molecular map
    map_ = read("map.sbgn").obj

    # Render the map to an image
    render_map(
        map_,
        "output.svg",
    )
    ```
"""
