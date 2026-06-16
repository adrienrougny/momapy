"""Generic reusable shapes, nodes, and arcs.

This package intentionally re-exports nothing: the submodules
`momapy.meta.shapes`, `momapy.meta.nodes`, and `momapy.meta.arcs` define
many overlapping names (e.g. ``Rectangle``, ``Ellipse``, ``Triangle``
each exist in all three), so a flat re-export would force renames. Access
these classes via their submodule, e.g. ``momapy.meta.shapes.Rectangle``,
``momapy.meta.nodes.Rectangle``, ``momapy.meta.arcs.Triangle``.
"""
