"""Library for working with molecular maps programmatically.

This package provides tools for reading, writing, manipulating, and rendering
molecular maps, with support for various formats including SBGN-ML and CellDesigner.

Example:
    >>> from momapy.io.core import read
    >>> from momapy.rendering.core import render_layout_elements
    >>> # Read a molecular map
    >>> result = read("map.sbgn", return_type="layout")
    >>> layout = result.obj
    >>> # Render the map to an image
    >>> render_layout_elements(
    ...     layout_elements=[layout],
    ...     file_path="output.svg",
    ...     format_="svg"
    ... )
"""
