"""Command-line interface for momapy.

This module provides a CLI for working with molecular maps, including commands
for rendering maps to various image formats.

Example:
    # Render an SBGN-ML file to SVG
    $ momapy render map.sbgn -o output.svg

    # Render with a specific renderer
    $ momapy render map.sbgn -o output.pdf -r cairo

    # Apply a style sheet
    $ momapy render map.sbgn -o output.svg -s custom_style.css
"""

import argparse
import pathlib


def run(args):
    """Execute the CLI command based on parsed arguments.

    Args:
        args: Parsed command-line arguments with subcommand and options.

    Raises:
        ValueError: If the subcommand is not supported.

    Example:
        >>> import argparse
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("subcommand", default="render")
        >>> args = parser.parse_args(["render"])
        >>> run(args)  # Executes the render command
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
            layout = momapy.io.core.read(input_file_path, return_type="layout").obj
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
    else:
        raise ValueError(f"subcommand {args.subcommand} not supported")


def main():
    """Parse command-line arguments and run the appropriate command.

    This function sets up the argument parser with subcommands and options,
    then calls run() with the parsed arguments.

    Returns:
        None

    Example:
        # From command line:
        $ python -m momapy.cli render input.sbgn -o output.svg
    """
    parser = argparse.ArgumentParser(
        description="Tool for working with molecular maps. Currently, only the 'render' subcommand is supported.",
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
        "-s",
        "--style-sheet-file-path",
        action="append",
        default=[],
        help="style sheet file path",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
