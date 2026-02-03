import argparse
import pathlib


def run(args):
    if args.subcommand == "render":
        import momapy.io.core
        import momapy.rendering.core
        import momapy.rendering.svg_native

        momapy.rendering._ensure_registered()
        try:
            import momapy.rendering.skia
        except Exception:
            pass
        try:
            import momapy.rendering.cairo
        except Exception:
            pass
        if args.format is None:
            output_file_path = pathlib.Path(args.output)
            format_ = output_file_path.suffix[1:]
        else:
            format_ = args.format
        if args.renderer is None:
            renderer = "svg-native"
            for candidate_renderer in ["svg-native", "skia", "cairo"]:
                if (
                    candidate_renderer in momapy.rendering.core.renderers
                    and format_
                    in momapy.rendering.core.renderers[
                        candidate_renderer
                    ].supported_formats
                ):
                    renderer = candidate_renderer
                    break
        else:
            renderer = args.renderer
        if args.style_sheet:
            style_sheets = [
                momapy.styling.StyleSheet.from_file(file_path)
                for file_path in args.style_sheet
            ]
            if len(style_sheets) > 1:
                style_sheet = momapy.styling.combine_style_sheets(style_sheets)
            else:
                style_sheet = style_sheets[0]
        else:
            style_sheet = None
        layouts = []
        for input_file_path in args.input_file_paths:
            layout = momapy.io.core.read(input_file_path, return_type="layout").obj
            layouts.append(layout)
        momapy.rendering.core.render_layout_elements(
            layout_elements=layouts,
            file_path=args.output,
            format_=format_,
            renderer=renderer,
            style_sheet=style_sheet,
            to_top_left=args.to_top_left,
            multi_pages=args.multi_pages,
        )
    else:
        raise ValueError(f"subcommand {args.subcommand} not supported")


def main():
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
