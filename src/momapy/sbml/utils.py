"""Utility functions for SBML map manipulation.

This module provides helper functions for summarizing SBML maps. SBML is
read-only in momapy and carries no layout, so the utilities here operate on
the model only.
"""

import typing

from momapy.sbml.map import SBMLMap

__all__ = ["get_info"]


def get_info(map_: SBMLMap) -> dict[str, typing.Any]:
    """Get a summary of the contents of an SBML map.

    SBML maps have no layout, so the returned ``layout`` value is ``None``.

    Args:
        map_: An SBML map.

    Returns:
        A dictionary with keys ``map_type``, ``model``, and ``layout``. The
        ``model`` entry is ``None`` when the map has no model (e.g. after
        ``read(..., with_model=False)``), and ``layout`` is always ``None``.
    """
    model = map_.model
    if model is None:
        model_info = None
    else:
        model_info = {
            "compartments": len(model.compartments),
            "species": len(model.species),
            "reactions": len(model.reactions),
        }
    return {
        "map_type": "SBML",
        "model": model_info,
        "layout": None,
    }
