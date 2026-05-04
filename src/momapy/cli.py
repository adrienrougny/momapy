"""Command-line interface for momapy.

This module provides a CLI for working with molecular maps, including commands
for rendering maps to various image formats, exporting maps to their
original format (useful for roundtrip testing), listing available plugins,
and interactively visualizing maps in the browser.

Example:
    # Render an SBGN-ML file to SVG
    $ momapy render map.sbgn -o output.svg

    # Render with a specific renderer
    $ momapy render map.sbgn -o output.pdf -r cairo

    # Apply a style sheet
    $ momapy render map.sbgn -o output.svg -s custom_style.css

    # Export a CellDesigner map (roundtrip)
    $ momapy export map.xml -o output.xml

    # Export with tidy and style sheet
    $ momapy export map.sbgn -o output.sbgn -t -s style.css

    # List available readers, writers, or renderers
    $ momapy list readers
    $ momapy list writers
    $ momapy list renderers

    # List stylable attributes of a layout element class
    $ momapy list attributes momapy.sbgn.pd:MacromoleculeLayout
    $ momapy list attributes momapy.sbgn.pd.MacromoleculeLayout -p

    # Inspect a map file
    $ momapy info map.sbgn
    $ momapy info map.xml --format json

    # Open an interactive viewer in the browser
    $ momapy visualize map.sbgn
    $ momapy visualize map.xml -t -s style.css

    # Tidy operations
    $ momapy tidy all map.xml -o output.xml
    $ momapy tidy fit-species map.xml -o output.xml --xsep 4 --ysep 4
    $ momapy tidy fit-epns map.sbgn -o output.sbgn --xsep 4 --ysep 4
    $ momapy tidy snap-arcs map.xml -o output.xml
    $ momapy tidy straighten-arcs map.xml -o output.xml --angle-tolerance 5
    $ momapy tidy fit-complexes map.sbgn -o output.sbgn --xsep 10 --ysep 10

    # Apply styling
    $ momapy style map.sbgn -p sbgned -o styled.sbgn
    $ momapy style map.sbgn -s custom.css -o styled.sbgn
    $ momapy style map.sbgn -p cs_default -s tweaks.css -p fs_shadows -o styled.sbgn

    # List available named colors
    $ momapy list colors

    # List available style presets
    $ momapy list styles

    # Piping between commands
    $ momapy export map.xml | momapy render -o output.svg
    $ momapy export map.xml | momapy tidy fit-nodes | momapy render -o output.svg
    $ momapy style map.sbgn -p newt | momapy render -o output.svg
    $ momapy export map.xml | momapy style -p cs_default | momapy render -o output.svg
    $ cat map.sbgn | momapy render -o output.svg
"""

import argparse
import base64
import collections.abc
import dataclasses
import importlib
import importlib.resources
import json
import os
import pathlib
import pickle
import string
import sys
import tempfile
import webbrowser

import momapy.celldesigner.utils
import momapy.sbgn.af
import momapy.sbgn
import momapy.sbgn.pd
import momapy.sbgn.utils
from momapy.celldesigner.map import CellDesignerMap
from momapy.celldesigner.layout import (
    ComplexActiveLayout,
    ComplexLayout,
    ModificationLayout,
    OvalCompartmentLayout,
    RectangleCompartmentLayout,
    StructuralStateLayout,
)


_BUILTIN_PRESETS = {
    "cs_default": (
        "Default colorscheme",
        "momapy.sbgn.styling",
        "cs_default",
    ),
    "cs_black_and_white": (
        "Black and white colorscheme",
        "momapy.sbgn.styling",
        "cs_black_and_white",
    ),
    "sbgned": (
        "SBGN-ED style",
        "momapy.sbgn.styling",
        "sbgned",
    ),
    "newt": (
        "Newt style",
        "momapy.sbgn.styling",
        "newt",
    ),
    "fs_shadows": (
        "Drop shadows",
        "momapy.sbgn.styling",
        "fs_shadows",
    ),
}


class _AppendStyleSource(argparse.Action):
    """Custom action to append style sources preserving CLI order.

    Both ``-s`` and ``-p`` flags append ``(source_type, value)`` tuples
    to a shared ``style_sources`` list on the namespace, so the
    interleaved order is preserved for merging.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, "style_sources") or namespace.style_sources is None:
            namespace.style_sources = []
        namespace.style_sources.append((self.const, values))


def _translate_layout_element(layout_element, translation_x, translation_y):
    """Recursively translate all positions in a layout element builder.

    Walks the layout element tree and shifts all positional attributes
    (node positions, text positions, arc segment points) by the given
    translation amounts. Operates on builders in place.

    Args:
        layout_element: A layout element builder to translate.
        translation_x: The horizontal translation amount.
        translation_y: The vertical translation amount.
    """
    import momapy.core.layout
    import momapy.geometry

    if hasattr(layout_element, "position"):
        layout_element.position = momapy.geometry.Point(
            layout_element.position.x + translation_x,
            layout_element.position.y + translation_y,
        )
    if hasattr(layout_element, "label") and layout_element.label is not None:
        layout_element.label.position = momapy.geometry.Point(
            layout_element.label.position.x + translation_x,
            layout_element.label.position.y + translation_y,
        )
    if hasattr(layout_element, "segments"):
        new_segments = []
        for segment in layout_element.segments:
            new_point_attributes = {}
            for attribute_name in [
                "p1",
                "p2",
                "control_point",
                "control_point1",
                "control_point2",
            ]:
                if hasattr(segment, attribute_name):
                    point = getattr(segment, attribute_name)
                    new_point_attributes[attribute_name] = momapy.geometry.Point(
                        point.x + translation_x,
                        point.y + translation_y,
                    )
            new_segments.append(dataclasses.replace(segment, **new_point_attributes))
        layout_element.segments = new_segments
    for child in layout_element.children():
        if child is not None:
            _translate_layout_element(child, translation_x, translation_y)


def _move_map_to_top_left(map_):
    """Translate all layout element positions so the layout starts at (0, 0).

    Computes the layout bounding box, then translates all positions by
    the negative of the top-left corner coordinates.

    Args:
        map_: The map object to translate.

    Returns:
        A new map with all layout positions translated to the top left.
    """
    import momapy.builder

    bbox = map_.layout.bbox()
    min_x = bbox.x - bbox.width / 2
    min_y = bbox.y - bbox.height / 2
    if min_x == 0 and min_y == 0:
        return map_
    map_builder = momapy.builder.builder_from_object(map_)
    _translate_layout_element(map_builder.layout, -min_x, -min_y)
    return momapy.builder.object_from_builder(map_builder)


def _infer_writer(map_):
    """Infer the writer name from the map type.

    Args:
        map_: The map object to infer the writer for.

    Returns:
        The name of the writer to use.

    Raises:
        ValueError: If the map type is not supported for export.
    """
    if isinstance(map_, CellDesignerMap):
        return "celldesigner"
    elif isinstance(map_, momapy.sbgn.SBGNMap):
        return "sbgnml"
    else:
        raise ValueError(f"could not infer writer for map type {type(map_).__name__}")


def _run_tidy_operation(map_, args):
    """Run a specific tidy operation on a map.

    Args:
        map_: The map object.
        args: Parsed CLI arguments with tidy_operation and parameters.

    Returns:
        The tidied map.

    Raises:
        ValueError: If the operation is not supported for the map type.
    """
    operation = args.tidy_operation
    is_celldesigner = isinstance(map_, CellDesignerMap)
    is_sbgn = isinstance(map_, momapy.sbgn.SBGNMap)
    if not is_celldesigner and not is_sbgn:
        raise ValueError(f"unsupported map type for tidy: {type(map_).__name__}")
    _default_sep = {
        "all": (4, 4),
        "fit-species": (4, 4),
        "fit-epns": (4, 4),
        "fit-auxiliary": (2, 2),
        "fit-complexes": (10, 10),
        "fit-compartments": (25, 25),
        "fit-submaps": (0, 0),
        "fit-layout": (0, 0),
    }
    default_xsep, default_ysep = _default_sep.get(operation, (0, 0))
    xsep_raw = getattr(args, "xsep", None)
    ysep_raw = getattr(args, "ysep", None)
    xsep = xsep_raw if xsep_raw is not None else default_xsep
    ysep = ysep_raw if ysep_raw is not None else default_ysep
    snap_arcs = not getattr(args, "no_snap_arcs", False)
    if operation == "all":
        if is_celldesigner:
            return momapy.celldesigner.utils.tidy(
                map_,
                nodes_xsep=xsep,
                nodes_ysep=ysep,
                arcs_angle_tolerance=getattr(args, "angle_tolerance", 5.0),
            )
        else:
            return momapy.sbgn.utils.tidy(map_, nodes_xsep=xsep, nodes_ysep=ysep)
    elif operation == "fit-species":
        if not is_celldesigner:
            raise ValueError(
                "fit-species is only supported for CellDesigner maps; "
                "use fit-epns for SBGN maps"
            )
        return momapy.celldesigner.utils.set_nodes_to_fit_labels(
            map_,
            xsep=xsep,
            ysep=ysep,
            exclude=[
                ModificationLayout,
                StructuralStateLayout,
                ComplexLayout,
                ComplexActiveLayout,
                OvalCompartmentLayout,
                RectangleCompartmentLayout,
            ],
            snap_arcs=snap_arcs,
        )
    elif operation == "fit-epns":
        if not is_sbgn:
            raise ValueError(
                "fit-epns is only supported for SBGN maps; "
                "use fit-species for CellDesigner maps"
            )
        return momapy.sbgn.utils.set_nodes_to_fit_labels(
            map_,
            xsep=xsep,
            ysep=ysep,
            exclude=[
                momapy.sbgn.pd.StateVariableLayout,
                momapy.sbgn.pd.UnitOfInformationLayout,
                momapy.sbgn.pd.ComplexLayout,
                momapy.sbgn.pd.CompartmentLayout,
                momapy.sbgn.af.UnitOfInformationLayout,
                momapy.sbgn.af.CompartmentLayout,
            ],
            snap_arcs=snap_arcs,
        )
    elif operation == "fit-auxiliary":
        if is_celldesigner:
            map_ = momapy.celldesigner.utils.set_modifications_to_borders(map_)
            return momapy.celldesigner.utils.set_nodes_to_fit_labels(
                map_,
                xsep=xsep,
                ysep=ysep,
                restrict_to=[
                    ModificationLayout,
                    StructuralStateLayout,
                ],
                snap_arcs=snap_arcs,
            )
        else:
            map_ = momapy.sbgn.utils.set_auxiliary_units_to_borders(map_)
            return momapy.sbgn.utils.set_nodes_to_fit_labels(
                map_,
                xsep=xsep,
                ysep=ysep,
                restrict_to=[
                    momapy.sbgn.pd.StateVariableLayout,
                    momapy.sbgn.pd.UnitOfInformationLayout,
                    momapy.sbgn.af.UnitOfInformationLayout,
                ],
                snap_arcs=snap_arcs,
            )
    elif operation == "fit-complexes":
        if is_celldesigner:
            return momapy.celldesigner.utils.set_complexes_to_fit_content(
                map_, xsep=xsep, ysep=ysep, snap_arcs=True
            )
        else:
            return momapy.sbgn.utils.set_complexes_to_fit_content(
                map_, xsep=xsep, ysep=ysep, snap_arcs=True
            )
    elif operation == "fit-compartments":
        if is_celldesigner:
            return momapy.celldesigner.utils.set_compartments_to_fit_content(
                map_, xsep=xsep, ysep=ysep, snap_arcs=True
            )
        else:
            return momapy.sbgn.utils.set_compartments_to_fit_content(
                map_, xsep=xsep, ysep=ysep, snap_arcs=True
            )
    elif operation == "fit-submaps":
        if is_sbgn:
            return momapy.sbgn.utils.set_submaps_to_fit_content(
                map_, xsep=xsep, ysep=ysep, snap_arcs=True
            )
        else:
            raise ValueError("fit-submaps is only supported for SBGN maps")
    elif operation == "fit-layout":
        if is_celldesigner:
            return momapy.celldesigner.utils.set_layout_to_fit_content(
                map_, xsep=xsep, ysep=ysep
            )
        else:
            return momapy.sbgn.utils.set_layout_to_fit_content(
                map_, xsep=xsep, ysep=ysep
            )
    elif operation == "snap-arcs":
        if is_celldesigner:
            return momapy.celldesigner.utils.set_arcs_to_borders(map_)
        else:
            return momapy.sbgn.utils.set_arcs_to_borders(map_)
    elif operation == "straighten-arcs":
        if is_celldesigner:
            return momapy.celldesigner.utils.straighten_arcs(
                map_,
                angle_tolerance=getattr(args, "angle_tolerance", 5.0),
            )
        else:
            raise ValueError("straighten-arcs is only supported for CellDesigner maps")
    else:
        raise ValueError(f"unknown tidy operation: {operation}")


def _read_input(input_file_path):
    """Read a map from a file path, or from stdin if path is None.

    When ``input_file_path`` is ``None``, reads binary data from stdin,
    buffers it to a temporary file, and uses the standard
    ``momapy.io.core.read()`` auto-detection (content-based
    ``check_file()``) to identify the format.

    Args:
        input_file_path: Path to the input file, or ``None`` to read
            from stdin.

    Returns:
        A ``ReaderResult`` containing the parsed map and metadata.
    """
    import momapy.io.core

    if input_file_path is not None:
        return momapy.io.core.read(input_file_path)
    if sys.stdin.isatty():
        print(
            "error: no input file and stdin is not a pipe",
            file=sys.stderr,
        )
        sys.exit(1)
    temporary_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        data = sys.stdin.buffer.read()
        if not data:
            print("error: no input received on stdin", file=sys.stderr)
            sys.exit(1)
        temporary_file.write(data)
        temporary_file.close()
        return momapy.io.core.read(temporary_file.name)
    finally:
        os.remove(temporary_file.name)


def _write_xml_to_stdout(map_, writer):
    """Write a map as XML to stdout using a temporary file.

    Args:
        map_: The map object to write.
        writer: The writer name to use (e.g. ``"sbgnml"``,
            ``"celldesigner"``).
    """
    import momapy.io.core

    temporary_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False)
    temporary_file_path = temporary_file.name
    temporary_file.close()
    try:
        momapy.io.core.write(map_, temporary_file_path, writer=writer)
        with open(temporary_file_path, "r") as file_handle:
            sys.stdout.write(file_handle.read())
    finally:
        os.remove(temporary_file_path)


def _write_output(map_, reader_result, output_file_path):
    """Write a map to a file or to stdout.

    When ``output_file_path`` is given, writes to that file. Otherwise,
    if stdout is a pipe, pickles the ``ReaderResult`` (for downstream
    momapy commands). If stdout is a TTY, writes human-readable XML.

    Args:
        map_: The (possibly modified) map object to write.
        reader_result: The original ``ReaderResult`` whose metadata
            (annotations, notes, ID mappings) is preserved in the
            pickled output.
        output_file_path: Path to the output file, or ``None`` for
            stdout.
    """
    import momapy.io.core

    writer = _infer_writer(map_)
    if output_file_path:
        momapy.io.core.write(map_, output_file_path, writer=writer)
        return
    if not sys.stdout.isatty():
        updated_result = dataclasses.replace(reader_result, obj=map_)
        pickle.dump(updated_result, sys.stdout.buffer)
        return
    _write_xml_to_stdout(map_, writer)


def _build_layout_to_model_id_mapping(layout_model_mapping):
    """Build a dict mapping layout element IDs to model element IDs.

    Iterates the layout-model mapping and extracts the ``id_`` of each
    layout element and its corresponding model element. For frozenset keys,
    each layout element in the set is mapped. For tuple values (child
    elements), the child model element's ``id_`` is used.

    Args:
        layout_model_mapping: The layout-model mapping from the map, or
            ``None`` if unavailable.

    Returns:
        A dictionary mapping layout element ``id_`` strings to model
        element ``id_`` strings.
    """
    if layout_model_mapping is None:
        return {}
    layout_id_to_model_id = {}
    singleton_to_key = layout_model_mapping._singleton_to_key
    # First pass: frozenset keys (processes, modulations).
    # Only map the anchor element of each frozenset, not all
    # participants, to avoid overwriting other elements' model IDs.
    for key, value in layout_model_mapping.items():
        if not isinstance(key, frozenset):
            continue
        if isinstance(value, tuple):
            model_id = str(value[0].id_)
        else:
            model_id = str(value.id_)
        for layout_element in key:
            if singleton_to_key.get(layout_element) == key:
                layout_id_to_model_id[str(layout_element.id_)] = model_id
    # Second pass: singleton keys override frozenset entries,
    # so each element gets its own model ID when available.
    for key, value in layout_model_mapping.items():
        if isinstance(key, frozenset):
            continue
        if isinstance(value, tuple):
            model_id = str(value[0].id_)
        else:
            model_id = str(value.id_)
        layout_id_to_model_id[str(key.id_)] = model_id
    return layout_id_to_model_id


def _extract_element_metadata(
    layout_element,
    layout_id_to_model_id=None,
    parent_id=None,
):
    """Recursively extract metadata from a layout element tree.

    Walks the layout element and its children, building a flat dictionary
    keyed by element ``id_`` (the same UUIDs used as SVG ``id`` attributes).

    Args:
        layout_element: The root layout element to extract metadata from.
        layout_id_to_model_id: A mapping from layout element IDs to model
            element IDs, or ``None`` if unavailable.
        parent_id: The ``id_`` of the parent element, or ``None`` for the
            root.

    Returns:
        A dictionary mapping element IDs to metadata dicts with keys
        ``type``, ``label``, ``model_id``, and ``parent_id``.
    """
    import momapy.core.layout

    if layout_id_to_model_id is None:
        layout_id_to_model_id = {}
    metadata = {}
    element_id = str(layout_element.id_)
    element_type = type(layout_element).__name__
    label_text = None
    if (
        isinstance(layout_element, momapy.core.layout.Node)
        and layout_element.label is not None
    ):
        label_text = layout_element.label.text
    elif isinstance(layout_element, momapy.core.layout.TextLayout):
        label_text = layout_element.text
    model_id = layout_id_to_model_id.get(element_id)
    metadata[element_id] = {
        "type": element_type,
        "label": label_text,
        "model_id": model_id,
        "parent_id": parent_id,
    }
    for child in layout_element.children():
        if child is not None:
            child_metadata = _extract_element_metadata(
                child,
                layout_id_to_model_id=layout_id_to_model_id,
                parent_id=element_id,
            )
            metadata.update(child_metadata)
    return metadata


def _render_svg_string(layout_element, style_sheet=None, to_top_left=False):
    """Render a layout element to an SVG string.

    Uses the native SVG renderer directly without writing to a file.
    Replicates the essential preparation logic from
    ``momapy.rendering.core.render_layout_elements``.

    Args:
        layout_element: The layout element to render.
        style_sheet: An optional style sheet to apply before rendering.
        to_top_left: Whether to move the layout element to the top left
            before rendering. Defaults to ``False``.

    Returns:
        The SVG markup as a string.
    """
    import momapy.builder
    import momapy.geometry
    import momapy.rendering.svg_native
    import momapy.styling

    bbox = layout_element.bbox()
    maximum_x = bbox.x + bbox.width / 2
    maximum_y = bbox.y + bbox.height / 2
    if style_sheet is not None or to_top_left:
        layout_element = momapy.builder.builder_from_object(layout_element)
        if style_sheet is not None:
            if (
                not isinstance(style_sheet, collections.abc.Collection)
                or isinstance(style_sheet, str)
                or isinstance(style_sheet, momapy.styling.StyleSheet)
            ):
                style_sheets = [style_sheet]
            else:
                style_sheets = list(style_sheet)
            style_sheets = [
                (
                    momapy.styling.StyleSheet.from_file(single_style_sheet)
                    if not isinstance(single_style_sheet, momapy.styling.StyleSheet)
                    else single_style_sheet
                )
                for single_style_sheet in style_sheets
            ]
            combined_style_sheet = momapy.styling.combine_style_sheets(style_sheets)
            momapy.styling.apply_style_sheet(layout_element, combined_style_sheet)
        if to_top_left:
            min_x = bbox.x - bbox.width / 2
            min_y = bbox.y - bbox.height / 2
            maximum_x -= min_x
            maximum_y -= min_y
            translation = momapy.geometry.Translation(-min_x, -min_y)
            for attribute_name in ["group_transform", "transform"]:
                if hasattr(layout_element, attribute_name):
                    if getattr(layout_element, attribute_name) is None:
                        setattr(layout_element, attribute_name, [])
                    getattr(layout_element, attribute_name).append(translation)
                    break
    svg_element = momapy.rendering.svg_native.SVGElement(
        name="svg",
        attributes={
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {maximum_x} {maximum_y}",
        },
    )
    renderer = momapy.rendering.svg_native.SVGNativeRenderer(
        svg=svg_element,
        config={},
    )
    renderer.begin_session()
    renderer.render_layout_element(layout_element)
    renderer.end_session()
    return str(renderer.svg)


_VISUALIZE_HTML_TEMPLATE = string.Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" type="image/png" href="$favicon_data_uri">
<title>$page_title</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { overflow: hidden; font-family: system-ui, -apple-system, sans-serif; background: #f0f0f0; }
#toolbar {
    position: fixed; top: 0; left: 0; right: 0; height: 44px;
    background: #fff; border-bottom: 1px solid #d0d0d0;
    display: flex; align-items: center; padding: 0 16px; z-index: 100;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    gap: 12px;
}
#toolbar-title {
    font-size: 14px; font-weight: 600; color: #333;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    max-width: 300px;
}
#search-input {
    width: 280px; padding: 6px 10px; font-size: 13px;
    border: 1px solid #ccc; border-radius: 4px; outline: none;
}
#search-input:focus { border-color: #4a90d9; box-shadow: 0 0 0 2px rgba(74,144,217,0.2); }
#search-count { font-size: 12px; color: #888; white-space: nowrap; }
#zoom-info { font-size: 12px; color: #888; margin-left: auto; white-space: nowrap; }
#svg-container {
    position: absolute; top: 44px; left: 0; right: 0; bottom: 0;
    overflow: hidden; background: #f8f8f8;
}
#svg-container.dragging, #svg-container.dragging svg, #svg-container.dragging svg * { cursor: grabbing !important; }
#svg-container svg { display: block; width: 100%; height: 100%; cursor: default; }
#svg-container svg text { cursor: default; }
#tooltip {
    position: fixed; background: rgba(30,30,30,0.92); color: #fff;
    padding: 8px 12px; border-radius: 6px; font-size: 12px;
    pointer-events: none; display: none; z-index: 200;
    max-width: 450px; line-height: 1.5; font-family: monospace;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
#tooltip .tooltip-type { color: #8be9fd; }
#tooltip .tooltip-id { color: #f1fa8c; }
#tooltip .tooltip-label { color: #50fa7b; }
#tooltip .tooltip-model-id { color: #bd93f9; }
.search-dim { opacity: 0.15; }
#info-panel {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #1e1e1e; color: #fff; font-family: monospace; font-size: 13px;
    padding: 10px 16px; z-index: 100; display: none;
    border-top: 1px solid #444; line-height: 1.6;
    user-select: text; -webkit-user-select: text;
}
#info-panel .info-row { display: inline-block; margin-right: 24px; }
#info-panel .info-key { color: #888; }
#info-panel .info-value { color: #fff; }
#info-panel .info-type .info-value { color: #8be9fd; }
#info-panel .info-layout-id .info-value { color: #f1fa8c; }
#info-panel .info-model-id .info-value { color: #bd93f9; }
#info-panel .info-label .info-value { color: #50fa7b; }
#info-panel-close {
    position: absolute; top: 8px; right: 12px;
    background: none; border: none; color: #888; font-size: 18px;
    cursor: pointer; line-height: 1;
}
#info-panel-close:hover { color: #fff; }
</style>
</head>
<body>
<div id="toolbar">
    <span id="toolbar-title">$toolbar_title</span>
    <input id="search-input" type="text" placeholder="Search by label or ID..." />
    <span id="search-count"></span>
    <span id="zoom-info">100%</span>
</div>
<div id="svg-container">
$svg_content
</div>
<div id="tooltip"></div>
<div id="info-panel">
    <button id="info-panel-close">&times;</button>
</div>
<script>
(function() {
    "use strict";

    var ELEMENT_METADATA = $element_metadata_json;

    // --- SVG and viewBox setup ---
    var container = document.getElementById("svg-container");
    var svgElement = container.querySelector("svg");
    var tooltip = document.getElementById("tooltip");
    var infoPanel = document.getElementById("info-panel");
    var searchInput = document.getElementById("search-input");
    var searchCount = document.getElementById("search-count");
    var zoomInfo = document.getElementById("zoom-info");

    var originalViewBox = svgElement.getAttribute("viewBox").split(" ").map(Number);
    var viewBox = { x: originalViewBox[0], y: originalViewBox[1],
                    width: originalViewBox[2], height: originalViewBox[3] };
    var initialWidth = viewBox.width;

    function applyViewBox() {
        svgElement.setAttribute("viewBox",
            viewBox.x + " " + viewBox.y + " " + viewBox.width + " " + viewBox.height);
        var zoomPercent = Math.round((initialWidth / viewBox.width) * 100);
        zoomInfo.textContent = zoomPercent + "%";
    }

    // --- Pan ---
    var isDragging = false;
    var dragStart = { x: 0, y: 0 };
    var viewBoxStart = { x: 0, y: 0 };

    container.addEventListener("mousedown", function(event) {
        if (event.button !== 0) return;
        isDragging = true;
        container.classList.add("dragging");
        dragStart.x = event.clientX;
        dragStart.y = event.clientY;
        viewBoxStart.x = viewBox.x;
        viewBoxStart.y = viewBox.y;
        event.preventDefault();
    });

    window.addEventListener("mousemove", function(event) {
        if (!isDragging) return;
        var containerRect = container.getBoundingClientRect();
        var scaleX = viewBox.width / containerRect.width;
        var scaleY = viewBox.height / containerRect.height;
        viewBox.x = viewBoxStart.x - (event.clientX - dragStart.x) * scaleX;
        viewBox.y = viewBoxStart.y - (event.clientY - dragStart.y) * scaleY;
        applyViewBox();
    });

    window.addEventListener("mouseup", function() {
        isDragging = false;
        container.classList.remove("dragging");
    });

    // --- Zoom ---
    container.addEventListener("wheel", function(event) {
        event.preventDefault();
        var zoomFactor = event.deltaY > 0 ? 1.1 : 0.9;
        var containerRect = container.getBoundingClientRect();
        var mouseX = (event.clientX - containerRect.left) / containerRect.width;
        var mouseY = (event.clientY - containerRect.top) / containerRect.height;

        var newWidth = viewBox.width * zoomFactor;
        var newHeight = viewBox.height * zoomFactor;

        // Clamp zoom: 5% to 2000% of original
        if (newWidth < initialWidth * 0.05 || newWidth > initialWidth * 20) return;

        viewBox.x += (viewBox.width - newWidth) * mouseX;
        viewBox.y += (viewBox.height - newHeight) * mouseY;
        viewBox.width = newWidth;
        viewBox.height = newHeight;
        applyViewBox();
    }, { passive: false });

    // --- Element lookup helpers ---
    function findMetadataElement(target) {
        var element = target;
        while (element && element !== svgElement) {
            if (element.id && ELEMENT_METADATA[element.id]) {
                return element;
            }
            element = element.parentElement;
        }
        return null;
    }

    function resolveMetadata(target) {
        var metadataElement = findMetadataElement(target);
        if (!metadataElement) return null;
        var metadata = ELEMENT_METADATA[metadataElement.id];
        if (metadata.type === "TextLayout" && metadata.parent_id) {
            var parentElement = document.getElementById(metadata.parent_id);
            if (parentElement && ELEMENT_METADATA[metadata.parent_id]) {
                metadataElement = parentElement;
                metadata = ELEMENT_METADATA[metadata.parent_id];
            }
        }
        return { element: metadataElement, metadata: metadata };
    }

    // --- Tooltip ---
    container.addEventListener("mousemove", function(event) {
        if (isDragging) {
            tooltip.style.display = "none";
            return;
        }
        var target = document.elementFromPoint(event.clientX, event.clientY);
        if (!target) {
            tooltip.style.display = "none";
            return;
        }
        var resolved = resolveMetadata(target);
        if (!resolved) {
            tooltip.style.display = "none";
            return;
        }
        var metadata = resolved.metadata;
        var elementId = resolved.element.id;

        var lines = [];
        lines.push('<span class="tooltip-type">Type: ' + metadata.type + '</span>');
        lines.push('<span class="tooltip-id">Layout ID: ' + elementId + '</span>');
        if (metadata.model_id) {
            lines.push('<span class="tooltip-model-id">Model ID: ' + metadata.model_id + '</span>');
        }
        if (metadata.label) {
            lines.push('<span class="tooltip-label">Label: ' + metadata.label + '</span>');
        }
        tooltip.innerHTML = lines.join("<br>");
        tooltip.style.display = "block";

        var tooltipX = event.clientX + 15;
        var tooltipY = event.clientY + 15;
        var tooltipRect = tooltip.getBoundingClientRect();
        if (tooltipX + tooltipRect.width > window.innerWidth - 10) {
            tooltipX = event.clientX - tooltipRect.width - 15;
        }
        if (tooltipY + tooltipRect.height > window.innerHeight - 10) {
            tooltipY = event.clientY - tooltipRect.height - 15;
        }
        tooltip.style.left = tooltipX + "px";
        tooltip.style.top = tooltipY + "px";
    });

    container.addEventListener("mouseleave", function() {
        tooltip.style.display = "none";
    });

    // --- Info panel on click ---
    container.addEventListener("click", function(event) {
        var target = document.elementFromPoint(event.clientX, event.clientY);
        if (!target) return;
        var resolved = resolveMetadata(target);
        if (!resolved) {
            infoPanel.style.display = "none";
            return;
        }
        var metadata = resolved.metadata;
        var elementId = resolved.element.id;
        var rows = [];
        rows.push('<span class="info-row info-type"><span class="info-key">Type: </span><span class="info-value">' + metadata.type + '</span></span>');
        rows.push('<span class="info-row info-layout-id"><span class="info-key">Layout ID: </span><span class="info-value">' + elementId + '</span></span>');
        if (metadata.model_id) {
            rows.push('<span class="info-row info-model-id"><span class="info-key">Model ID: </span><span class="info-value">' + metadata.model_id + '</span></span>');
        }
        if (metadata.label) {
            rows.push('<span class="info-row info-label"><span class="info-key">Label: </span><span class="info-value">' + metadata.label + '</span></span>');
        }
        infoPanel.innerHTML = '<button id="info-panel-close">&times;</button>' + rows.join("");
        infoPanel.style.display = "block";
        document.getElementById("info-panel-close").addEventListener("click", function() {
            infoPanel.style.display = "none";
        });
    });

    // --- Search ---
    var highlightedElements = [];
    var lastMatchingIds = [];

    function clearHighlights() {
        for (var i = 0; i < highlightedElements.length; i++) {
            highlightedElements[i].classList.remove("search-dim");
        }
        highlightedElements = [];
        lastMatchingIds = [];
        searchCount.textContent = "";
    }

    function performSearch(query) {
        clearHighlights();
        if (!query) return;

        var lowerQuery = query.toLowerCase();
        var matchingIds = [];
        var allIds = [];

        for (var elementId in ELEMENT_METADATA) {
            var metadata = ELEMENT_METADATA[elementId];
            // Skip TextLayout for search results
            if (metadata.type === "TextLayout") continue;

            allIds.push(elementId);
            var matches = false;
            if (metadata.label && metadata.label.toLowerCase().indexOf(lowerQuery) !== -1) {
                matches = true;
            }
            if (elementId.toLowerCase().indexOf(lowerQuery) !== -1) {
                matches = true;
            }
            if (matches) {
                matchingIds.push(elementId);
            }
        }

        if (matchingIds.length === 0) {
            searchCount.textContent = "no matches";
        }

        // Collect ancestors of matches (must not be fully dimmed,
        // but their own SVG children should be dimmed).
        var ancestorOfMatch = {};
        for (var j = 0; j < matchingIds.length; j++) {
            var id = ELEMENT_METADATA[matchingIds[j]].parent_id;
            while (id) {
                ancestorOfMatch[id] = true;
                id = ELEMENT_METADATA[id] ? ELEMENT_METADATA[id].parent_id : null;
            }
        }

        // Collect descendants of matches (must not be dimmed).
        var descendantOfMatch = {};
        function markDescendants(elementId) {
            var children = [];
            for (var id in ELEMENT_METADATA) {
                if (ELEMENT_METADATA[id].parent_id === elementId) children.push(id);
            }
            for (var c = 0; c < children.length; c++) {
                descendantOfMatch[children[c]] = true;
                markDescendants(children[c]);
            }
        }
        for (var j = 0; j < matchingIds.length; j++) {
            markDescendants(matchingIds[j]);
        }

        // Set of IDs that must stay fully visible
        var keepVisible = {};
        for (var j = 0; j < matchingIds.length; j++) keepVisible[matchingIds[j]] = true;
        for (var id in descendantOfMatch) keepVisible[id] = true;
        for (var id in ancestorOfMatch) keepVisible[id] = true;

        // Dim non-visible layout elements (skip root, avoid compounding)
        var dimmedSet = {};
        for (var i = 0; i < allIds.length; i++) {
            var elId = allIds[i];
            var meta = ELEMENT_METADATA[elId];
            if (!meta || meta.parent_id === null) continue;
            if (keepVisible[elId]) continue;
            var parentDimmed = false;
            var pid = meta.parent_id;
            while (pid) {
                if (dimmedSet[pid]) { parentDimmed = true; break; }
                pid = ELEMENT_METADATA[pid] ? ELEMENT_METADATA[pid].parent_id : null;
            }
            if (parentDimmed) continue;
            var svgEl = document.getElementById(elId);
            if (svgEl) {
                svgEl.classList.add("search-dim");
                highlightedElements.push(svgEl);
                dimmedSet[elId] = true;
            }
        }

        // For ancestors of matches: dim their own SVG children that
        // are not a kept-visible layout element's group. This dims
        // the ancestor's shape and label without affecting the match.
        for (var id in ancestorOfMatch) {
            var svgGroup = document.getElementById(id);
            if (!svgGroup) continue;
            var svgChildren = svgGroup.children;
            for (var c = 0; c < svgChildren.length; c++) {
                var childId = svgChildren[c].id;
                if (!childId) continue;
                if (keepVisible[childId]) continue;
                if (dimmedSet[childId]) continue;
                svgChildren[c].classList.add("search-dim");
                highlightedElements.push(svgChildren[c]);
            }
        }

        lastMatchingIds = matchingIds;
        searchCount.textContent = matchingIds.length + " match" + (matchingIds.length !== 1 ? "es" : "");
    }

    searchInput.addEventListener("input", function() {
        performSearch(searchInput.value.trim());
    });

    searchInput.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            searchInput.value = "";
            clearHighlights();
            searchInput.blur();
            return;
        }
        if (event.key === "Enter" && lastMatchingIds.length > 0) {
            // Pan to first match
            var firstMatch = document.getElementById(lastMatchingIds[0]);
            if (firstMatch) {
                var bbox = firstMatch.getBBox();
                var padding = Math.max(bbox.width, bbox.height) * 0.5;
                viewBox.x = bbox.x - padding;
                viewBox.y = bbox.y - padding;
                viewBox.width = bbox.width + padding * 2;
                viewBox.height = bbox.height + padding * 2;
                applyViewBox();
            }
        }
    });

    // --- Keyboard shortcut: Ctrl+F / Cmd+F focuses search ---
    window.addEventListener("keydown", function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === "f") {
            event.preventDefault();
            searchInput.focus();
            searchInput.select();
        }
    });

    // --- Double-click to reset view ---
    container.addEventListener("dblclick", function() {
        viewBox.x = originalViewBox[0];
        viewBox.y = originalViewBox[1];
        viewBox.width = originalViewBox[2];
        viewBox.height = originalViewBox[3];
        applyViewBox();
    });

})();
</script>
</body>
</html>
""")


def _visualize_map(map_, style_sheet=None, input_file_path=None, to_top_left=False):
    """Render a map as an interactive HTML page and open it in the browser.

    Generates a self-contained HTML file with the map rendered as inline SVG,
    JavaScript for pan/zoom, hover tooltips, and search functionality, then
    opens it in the default web browser.

    Args:
        map_: The map to visualize.
        style_sheet: An optional style sheet to apply before rendering.
        input_file_path: The original input file path, used for the page
            title. If ``None``, a generic title is used.
        to_top_left: Whether to move the layout to the top left before
            rendering. Defaults to ``False``.
    """
    svg_string = _render_svg_string(
        map_.layout, style_sheet=style_sheet, to_top_left=to_top_left
    )
    layout_id_to_model_id = _build_layout_to_model_id_mapping(map_.layout_model_mapping)
    element_metadata = _extract_element_metadata(
        map_.layout,
        layout_id_to_model_id=layout_id_to_model_id,
    )
    element_metadata_json = json.dumps(element_metadata)
    if input_file_path is not None:
        map_file_name = pathlib.Path(input_file_path).name
        page_title = f"momapy — {map_file_name}"
        toolbar_title = map_file_name
    else:
        page_title = "momapy visualize"
        toolbar_title = "momapy visualize"
    favicon_bytes = (
        importlib.resources.files("momapy").joinpath("assets/favicon.png").read_bytes()
    )
    favicon_data_uri = "data:image/png;base64," + base64.b64encode(
        favicon_bytes
    ).decode("ascii")
    html_content = _VISUALIZE_HTML_TEMPLATE.substitute(
        page_title=page_title,
        toolbar_title=toolbar_title,
        favicon_data_uri=favicon_data_uri,
        svg_content=svg_string,
        element_metadata_json=element_metadata_json,
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        prefix="momapy_",
        delete=False,
        encoding="utf-8",
    ) as html_file:
        html_file.write(html_content)
        html_file_path = html_file.name
    print(f"Visualization saved to: {html_file_path}")
    webbrowser.open(f"file://{html_file_path}")


def _resolve_class(class_path):
    """Resolve a class from a string path.

    Accepts both colon notation (``module:Class``) and dotted notation
    (``module.Class``).

    Args:
        class_path: A string in the form ``module:Class`` or
            ``module.Class``.

    Returns:
        The resolved class object.

    Raises:
        argparse.ArgumentTypeError: If the module or class cannot be found.
    """
    if ":" in class_path:
        module_path, class_name = class_path.rsplit(":", 1)
    else:
        module_path, _, class_name = class_path.rpartition(".")
    if not module_path or not class_name:
        raise argparse.ArgumentTypeError(
            f"invalid class path: {class_path!r} "
            f"(expected 'module:Class' or 'module.Class')"
        )
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise argparse.ArgumentTypeError(f"module not found: {module_path!r}")
    try:
        cls = getattr(module, class_name)
    except AttributeError:
        raise argparse.ArgumentTypeError(
            f"class {class_name!r} not found in module {module_path!r}"
        )
    return cls


def run(args):
    """Execute the CLI command based on parsed arguments.

    Args:
        args: Parsed command-line arguments with subcommand and options.

    Raises:
        ValueError: If the subcommand is not supported.

    Examples:
        ```python
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("subcommand", default="render")
        args = parser.parse_args(["render"])
        run(args)  # Executes the render command
        ```
    """
    if args.subcommand == "render":
        import momapy.builder
        import momapy.io.core
        import momapy.rendering
        import momapy.rendering.core
        import momapy.styling

        format_ = args.format
        renderer = args.renderer
        if args.style_sheet_file_path:
            style_sheets = [
                momapy.styling.StyleSheet.from_file(style_sheet_file_path)
                for style_sheet_file_path in args.style_sheet_file_path
            ]
            if len(style_sheets) > 1:
                style_sheet = momapy.styling.combine_style_sheets(style_sheets)
            else:
                style_sheet = style_sheets[0]
        else:
            style_sheet = None
        layouts = []
        input_file_paths = args.input_file_path if args.input_file_path else [None]
        for input_file_path in input_file_paths:
            map_ = _read_input(input_file_path).obj
            if style_sheet is not None:
                map_builder = momapy.builder.builder_from_object(map_)
                momapy.styling.apply_style_sheet(map_builder.layout, style_sheet)
                map_ = momapy.builder.object_from_builder(map_builder)
            if args.tidy:
                if isinstance(map_, CellDesignerMap):
                    map_ = momapy.celldesigner.utils.tidy(map_)
                elif isinstance(map_, momapy.sbgn.SBGNMap):
                    map_ = momapy.sbgn.utils.tidy(map_)
            layout = map_.layout
            layouts.append(layout)
        momapy.rendering.core.render_layout_elements(
            layout_elements=layouts,
            file_path=args.output_file_path,
            format_=format_,
            renderer=renderer,
            to_top_left=args.to_top_left,
            multi_pages=args.multi_pages,
        )
    elif args.subcommand == "export":
        import momapy.builder
        import momapy.io.core
        import momapy.styling

        reader_result = _read_input(args.input_file_path)
        map_ = reader_result.obj
        if args.style_sheet_file_path:
            style_sheets = [
                momapy.styling.StyleSheet.from_file(style_sheet_file_path)
                for style_sheet_file_path in args.style_sheet_file_path
            ]
            if len(style_sheets) > 1:
                style_sheet = momapy.styling.combine_style_sheets(style_sheets)
            else:
                style_sheet = style_sheets[0]
            map_builder = momapy.builder.builder_from_object(map_)
            momapy.styling.apply_style_sheet(map_builder, style_sheet)
            map_ = map_builder.build()
        if args.tidy:
            if isinstance(map_, CellDesignerMap):
                map_ = momapy.celldesigner.utils.tidy(map_)
            elif isinstance(map_, momapy.sbgn.SBGNMap):
                map_ = momapy.sbgn.utils.tidy(map_)
        if args.to_top_left:
            map_ = _move_map_to_top_left(map_)
        _write_output(map_, reader_result, args.output_file_path)
    elif args.subcommand == "info":
        import momapy.io.core

        reader_result = _read_input(args.input_file_path)
        map_ = reader_result.obj
        if isinstance(map_, CellDesignerMap):
            info = momapy.celldesigner.utils.get_info(map_)
        elif isinstance(map_, momapy.sbgn.SBGNMap):
            info = momapy.sbgn.utils.get_info(map_)
        else:
            raise ValueError(f"unsupported map type: {type(map_).__name__}")
        info["file"] = str(args.input_file_path) if args.input_file_path else "<stdin>"
        if args.format == "json":
            output = json.dumps(info, indent=2)
        else:
            lines = []
            lines.append(f"File:      {info['file']}")
            lines.append(f"Map type:  {info['map_type']}")
            lines.append("")
            lines.append("Model:")
            for key, value in info["model"].items():
                label = key.replace("_", " ")
                lines.append(f"  {label + ':':<26s}{value}")
            lines.append("")
            lines.append("Layout:")
            lines.append(
                f"  {'dimensions:':<26s}"
                f"{info['layout']['width']} x {info['layout']['height']}"
            )
            lines.append(f"  {'elements:':<26s}{info['layout']['elements']}")
            output = "\n".join(lines)
        if args.output_file_path:
            with open(args.output_file_path, "w") as file_handle:
                file_handle.write(output + "\n")
        else:
            print(output)
    elif args.subcommand == "list":
        list_subcommand = args.list_subcommand
        if list_subcommand in ("readers", "writers", "renderers"):
            import momapy.io
            import momapy.rendering

            if list_subcommand == "readers":
                names = momapy.io.list_readers()
            elif list_subcommand == "writers":
                names = momapy.io.list_writers()
            else:
                names = momapy.rendering.list_renderers()
            if not names:
                print(f"No {list_subcommand} available.")
                return
            for name in names:
                line = name
                if list_subcommand == "renderers":
                    try:
                        renderer_cls = momapy.rendering.get_renderer(name)
                        formats = ", ".join(renderer_cls.supported_formats)
                        line = f"{name} (formats: {formats})"
                    except (ImportError, ModuleNotFoundError):
                        line = f"{name} (not installed)"
                print(line)
        elif list_subcommand == "colors":
            import momapy.coloring

            momapy.coloring.print_colors()
        elif list_subcommand == "styles":
            for name in sorted(_BUILTIN_PRESETS):
                description = _BUILTIN_PRESETS[name][0]
                print(f"{name:<25s}{description}")
        elif list_subcommand == "attributes":
            import momapy.styling

            try:
                attributes = momapy.styling.get_stylable_attributes(
                    args.class_path,
                    presentation_only=args.presentation_only,
                )
            except TypeError as exception:
                print(f"error: {exception}", file=sys.stderr)
                sys.exit(1)
            for attribute in attributes:
                print(attribute)
    elif args.subcommand == "tidy":
        import momapy.io.core

        reader_result = _read_input(args.input_file_path)
        map_ = reader_result.obj
        map_ = _run_tidy_operation(map_, args)
        _write_output(map_, reader_result, args.output_file_path)
    elif args.subcommand == "style":
        import momapy.builder
        import momapy.io.core
        import momapy.styling

        style_sources = getattr(args, "style_sources", None) or []
        if not style_sources:
            print(
                "error: at least one of -s or -p is required",
                file=sys.stderr,
            )
            sys.exit(1)
        style_sheets = []
        for source_type, value in style_sources:
            if source_type == "preset":
                if value not in _BUILTIN_PRESETS:
                    print(
                        f"error: unknown preset '{value}'; "
                        f"use 'momapy list styles' to see available presets",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                _, module_name, attribute_name = _BUILTIN_PRESETS[value]
                module = importlib.import_module(module_name)
                style_sheets.append(getattr(module, attribute_name))
            else:
                style_sheets.append(momapy.styling.StyleSheet.from_file(value))
        if len(style_sheets) > 1:
            style_sheet = momapy.styling.combine_style_sheets(style_sheets)
        else:
            style_sheet = style_sheets[0]
        reader_result = _read_input(args.input_file_path)
        map_ = reader_result.obj
        map_builder = momapy.builder.builder_from_object(map_)
        momapy.styling.apply_style_sheet(map_builder, style_sheet)
        map_ = map_builder.build()
        _write_output(map_, reader_result, args.output_file_path)
    elif args.subcommand == "visualize":
        import momapy.styling

        reader_result = _read_input(args.input_file_path)
        map_ = reader_result.obj
        style_sheet = None
        if args.style_sheet_file_path:
            style_sheets = [
                momapy.styling.StyleSheet.from_file(style_sheet_file_path)
                for style_sheet_file_path in args.style_sheet_file_path
            ]
            if len(style_sheets) > 1:
                style_sheet = momapy.styling.combine_style_sheets(style_sheets)
            else:
                style_sheet = style_sheets[0]
            map_builder = momapy.builder.builder_from_object(map_)
            momapy.styling.apply_style_sheet(map_builder.layout, style_sheet)
            map_ = momapy.builder.object_from_builder(map_builder)
        if args.tidy:
            if isinstance(map_, CellDesignerMap):
                map_ = momapy.celldesigner.utils.tidy(map_)
            elif isinstance(map_, momapy.sbgn.SBGNMap):
                map_ = momapy.sbgn.utils.tidy(map_)
        _visualize_map(
            map_=map_,
            input_file_path=args.input_file_path,
            to_top_left=args.to_top_left,
        )
    else:
        raise ValueError(f"subcommand {args.subcommand} not supported")


def main():
    """Parse command-line arguments and run the appropriate command.

    This function sets up the argument parser with subcommands and options,
    then calls run() with the parsed arguments.

    Returns:
        None

    Examples:
        ```bash
        # From command line:
        python -m momapy.cli render input.sbgn -o output.svg
        ```
    """
    parser = argparse.ArgumentParser(
        description="Tool for working with molecular maps.",
    )
    subparsers = parser.add_subparsers(dest="subcommand")
    render_parser = subparsers.add_parser(
        "render",
        description="Render a map (SBGN-ML or CellDesigner) to an output image file. If no format is specified, will base the format on the extension of the output file path. If no renderer is specified, will take the most appropriate renderer.",
    )
    render_parser.add_argument(
        "input_file_path",
        nargs="*",
        help="input file path (reads from stdin if omitted)",
    )
    render_parser.add_argument(
        "-o", "--output-file-path", required=True, help="output file path"
    )
    render_parser.add_argument(
        "-r",
        "--renderer",
        default=None,
        help="renderer to use",
    )
    render_parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="output file format",
    )
    render_parser.add_argument(
        "-m",
        "--multi-pages",
        action="store_true",
        default=False,
        help="render one map per page",
    )
    render_parser.add_argument(
        "-l",
        "--to-top-left",
        action="store_true",
        default=False,
        help="move the elements to the top left of the page",
    )
    render_parser.add_argument(
        "-t",
        "--tidy",
        action="store_true",
        default=False,
        help="tidy the map (reroute arcs, fit labels, etc.)",
    )
    render_parser.add_argument(
        "-s",
        "--style-sheet-file-path",
        action="append",
        default=[],
        help="style sheet file path",
    )
    export_parser = subparsers.add_parser(
        "export",
        description="Export a map (SBGN-ML or CellDesigner) to a file in the same format. Useful for roundtrip testing.",
    )
    export_parser.add_argument(
        "input_file_path",
        nargs="?",
        default=None,
        help="input file path (reads from stdin if omitted)",
    )
    export_parser.add_argument(
        "-o",
        "--output-file-path",
        default=None,
        help="output file path (default: stdout)",
    )
    export_parser.add_argument(
        "-t",
        "--tidy",
        action="store_true",
        default=False,
        help="tidy the map (reroute arcs, fit labels, etc.)",
    )
    export_parser.add_argument(
        "-l",
        "--to-top-left",
        action="store_true",
        default=False,
        help="move the elements to the top left of the page",
    )
    export_parser.add_argument(
        "-s",
        "--style-sheet-file-path",
        action="append",
        default=[],
        help="style sheet file path",
    )
    info_parser = subparsers.add_parser(
        "info",
        description="Print a summary of a map file's contents (map type, model element counts, layout dimensions).",
    )
    info_parser.add_argument(
        "input_file_path",
        nargs="?",
        default=None,
        help="input file path (reads from stdin if omitted)",
    )
    info_parser.add_argument(
        "-o",
        "--output-file-path",
        default=None,
        help="output file path (default: stdout)",
    )
    info_parser.add_argument(
        "-f",
        "--format",
        default="text",
        choices=["text", "json"],
        help="output format (default: text)",
    )
    list_parser = subparsers.add_parser(
        "list",
        description="List available plugins or stylable attributes.",
    )
    list_subparsers = list_parser.add_subparsers(
        dest="list_subcommand",
    )
    list_subparsers.add_parser(
        "readers",
        description="List available readers.",
    )
    list_subparsers.add_parser(
        "writers",
        description="List available writers.",
    )
    list_subparsers.add_parser(
        "renderers",
        description="List available renderers.",
    )
    list_subparsers.add_parser(
        "colors",
        description="List available named colors.",
    )
    list_subparsers.add_parser(
        "styles",
        description="List available built-in style presets.",
    )
    list_attributes_parser = list_subparsers.add_parser(
        "attributes",
        description="List stylable attributes of a layout element class.",
    )
    list_attributes_parser.add_argument(
        "class_path",
        type=_resolve_class,
        help="layout element class (e.g. momapy.sbgn.pd:MacromoleculeLayout)",
    )
    list_attributes_parser.add_argument(
        "-p",
        "--presentation-only",
        action="store_true",
        default=False,
        help="only list presentation attributes (fill, stroke, font, etc.)",
    )
    tidy_parser = subparsers.add_parser(
        "tidy",
        description="Apply layout tidying operations to a map. Use sub-commands to apply specific operations, or 'all' for the full pipeline.",
    )
    tidy_subparsers = tidy_parser.add_subparsers(
        dest="tidy_operation",
    )
    _tidy_operations = {
        "all": "Apply all tidying operations (fit nodes, decorations, complexes, compartments, arcs, layout).",
        "fit-species": "Resize species nodes to fit their labels (CellDesigner only).",
        "fit-epns": "Resize entity pool nodes to fit their labels (SBGN only).",
        "fit-auxiliary": "Position and resize auxiliary elements (modifications/structural states for CellDesigner, state variables/units of information for SBGN).",
        "fit-complexes": "Resize complexes to fit their subunits.",
        "fit-compartments": "Resize compartments to fit their content.",
        "fit-submaps": "Resize submaps to fit their terminals (SBGN only).",
        "fit-layout": "Resize the overall layout to fit all elements.",
        "snap-arcs": "Snap arc endpoints to node borders.",
        "straighten-arcs": "Straighten near-horizontal and near-vertical arc segments (CellDesigner only).",
    }
    for operation_name, operation_description in _tidy_operations.items():
        operation_parser = tidy_subparsers.add_parser(
            operation_name,
            description=operation_description,
        )
        operation_parser.add_argument(
            "input_file_path",
            nargs="?",
            default=None,
            help="input file path (reads from stdin if omitted)",
        )
        operation_parser.add_argument(
            "-o",
            "--output-file-path",
            default=None,
            help="output file path (default: stdout)",
        )
        if operation_name in (
            "all",
            "fit-species",
            "fit-epns",
            "fit-auxiliary",
            "fit-complexes",
            "fit-compartments",
            "fit-submaps",
            "fit-layout",
        ):
            operation_parser.add_argument(
                "--xsep",
                type=float,
                default=None,
                help="horizontal padding (default: depends on operation and map type)",
            )
            operation_parser.add_argument(
                "--ysep",
                type=float,
                default=None,
                help="vertical padding (default: depends on operation and map type)",
            )
        if operation_name in ("all", "straighten-arcs"):
            operation_parser.add_argument(
                "--angle-tolerance",
                type=float,
                default=5.0,
                help="angle tolerance in degrees for straightening (default: 5.0)",
            )
        if operation_name in (
            "fit-species",
            "fit-epns",
            "fit-auxiliary",
            "fit-complexes",
            "fit-compartments",
            "fit-submaps",
        ):
            operation_parser.add_argument(
                "--no-snap-arcs",
                action="store_true",
                default=False,
                help=(
                    "do not snap arc endpoints to node borders after "
                    "the operation (useful when chaining multiple tidy "
                    "operations; run 'tidy snap-arcs' once at the end)"
                ),
            )
    style_parser = subparsers.add_parser(
        "style",
        description=(
            "Apply CSS stylesheets to a map and output the styled map. "
            "Styles are baked into the map data (layout element attributes). "
            "Use -s for custom CSS files and -p for built-in presets. "
            "Multiple -s and -p flags can be interleaved; stylesheets are "
            "merged left-to-right (later overrides earlier)."
        ),
    )
    style_parser.add_argument(
        "input_file_path",
        nargs="?",
        default=None,
        help="input file path (reads from stdin if omitted)",
    )
    style_parser.add_argument(
        "-o",
        "--output-file-path",
        default=None,
        help="output file path (default: stdout)",
    )
    style_parser.add_argument(
        "-s",
        "--style-sheet-file-path",
        action=_AppendStyleSource,
        const="file",
        help="custom CSS style sheet file path (repeatable)",
    )
    style_parser.add_argument(
        "-p",
        "--preset",
        action=_AppendStyleSource,
        const="preset",
        help=(
            "built-in preset name (repeatable); "
            "use 'momapy list styles' to see available presets"
        ),
    )
    visualize_parser = subparsers.add_parser(
        "visualize",
        description="Open an interactive viewer for a molecular map in the default web browser.",
    )
    visualize_parser.add_argument(
        "input_file_path",
        nargs="?",
        default=None,
        help="input file path (reads from stdin if omitted)",
    )
    visualize_parser.add_argument(
        "-t",
        "--tidy",
        action="store_true",
        default=False,
        help="tidy the map (reroute arcs, fit labels, etc.)",
    )
    visualize_parser.add_argument(
        "-l",
        "--to-top-left",
        action="store_true",
        default=False,
        help="move the elements to the top left of the page",
    )
    visualize_parser.add_argument(
        "-s",
        "--style-sheet-file-path",
        action="append",
        default=[],
        help="style sheet file path",
    )
    args = parser.parse_args()
    try:
        run(args)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(141)


if __name__ == "__main__":
    main()
