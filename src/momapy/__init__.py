"""Library for working with molecular maps programmatically.

This package provides tools for reading, writing, manipulating, and rendering
molecular maps, with support for various formats including SBGN-ML and CellDesigner.

Example:
    >>> import momapy
    >>> # Read a molecular map
    >>> layout = momapy.io.core.read("map.sbgn", return_type="layout").obj
    >>> # Render the map to an image
    >>> momapy.rendering.core.render_layout_elements(
    ...     layout_elements=[layout],
    ...     file_path="output.svg",
    ...     format_="svg"
    ... )
"""
