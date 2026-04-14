"""Command-line interface for momapy.

This module provides a CLI for working with molecular maps, including commands
for rendering maps to various image formats, exporting maps to their
original format (useful for roundtrip testing), and listing available plugins.

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
    $ momapy export map.sbgn -o output.sbgn -c -s style.css

    # List available readers, writers, or renderers
    $ momapy list readers
    $ momapy list writers
    $ momapy list renderers
"""

import argparse
import momapy.celldesigner.core
import momapy.celldesigner.utils
import momapy.sbgn.core
import momapy.sbgn.utils


def _infer_writer(map_):
    """Infer the writer name from the map type.

    Args:
        map_: The map object to infer the writer for.

    Returns:
        The name of the writer to use.

    Raises:
        ValueError: If the map type is not supported for export.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return "celldesigner"
    elif isinstance(map_, momapy.sbgn.core.SBGNMap):
        return "sbgnml"
    else:
        raise ValueError(
            f"could not infer writer for map type {type(map_).__name__}"
        )


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
        for input_file_path in args.input_file_path:
            map_ = momapy.io.core.read(input_file_path).obj
            if args.tidy:
                if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
                    map_ = momapy.celldesigner.utils.tidy(map_)
                elif isinstance(map_, momapy.sbgn.core.SBGNMap):
                    map_ = momapy.sbgn.utils.tidy(map_)
            layout = map_.layout
            layouts.append(layout)
        momapy.rendering.core.render_layout_elements(
            layout_elements=layouts,
            file_path=args.output_file_path,
            format_=format_,
            renderer=renderer,
            style_sheet=style_sheet,
            to_top_left=args.to_top_left,
            multi_pages=args.multi_pages,
        )
    elif args.subcommand == "export":
        import momapy.builder
        import momapy.io.core
        import momapy.styling

        reader_result = momapy.io.core.read(args.input_file_path)
        map_ = reader_result.obj
        if args.tidy:
            if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
                map_ = momapy.celldesigner.utils.tidy(map_)
            elif isinstance(map_, momapy.sbgn.core.SBGNMap):
                map_ = momapy.sbgn.utils.tidy(map_)
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
        writer = _infer_writer(map_)
        momapy.io.core.write(map_, args.output_file_path, writer=writer)
    elif args.subcommand == "list":
        import momapy.io
        import momapy.rendering

        plugin_type = args.plugin_type
        if plugin_type == "readers":
            names = momapy.io.list_readers()
        elif plugin_type == "writers":
            names = momapy.io.list_writers()
        elif plugin_type == "renderers":
            names = momapy.rendering.list_renderers()
        else:
            raise ValueError(f"plugin type {plugin_type} not supported")
        if not names:
            print(f"No {plugin_type} available.")
            return
        for name in names:
            line = name
            if plugin_type == "renderers":
                try:
                    renderer_cls = momapy.rendering.get_renderer(name)
                    formats = ", ".join(renderer_cls.supported_formats)
                    line = f"{name} (formats: {formats})"
                except (ImportError, ModuleNotFoundError):
                    line = f"{name} (not installed)"
            print(line)
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
    render_parser.add_argument("input_file_path", nargs="+", help="input file path")
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
        "-t",
        "--to-top-left",
        action="store_true",
        default=False,
        help="move the elements to the top left of the page",
    )
    render_parser.add_argument(
        "-c",
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
    export_parser.add_argument("input_file_path", help="input file path")
    export_parser.add_argument(
        "-o", "--output-file-path", required=True, help="output file path"
    )
    export_parser.add_argument(
        "-c",
        "--tidy",
        action="store_true",
        default=False,
        help="tidy the map (reroute arcs, fit labels, etc.)",
    )
    export_parser.add_argument(
        "-s",
        "--style-sheet-file-path",
        action="append",
        default=[],
        help="style sheet file path",
    )
    list_parser = subparsers.add_parser(
        "list",
        description="List available readers, writers, or renderers.",
    )
    list_parser.add_argument(
        "plugin_type",
        choices=["readers", "writers", "renderers"],
        help="type of plugin to list",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
