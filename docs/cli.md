# CLI Reference

## Overview

The `momapy` command-line interface (CLI) allows you to render molecular maps directly from the command line without writing Python code. It supports SBGN-ML and CellDesigner map formats and can output to various image formats (SVG, PDF, PNG, JPEG, WebP).

## Synopsis

```bash
momapy render <input_file_path>... -o <output_file_path> [options]
```

## Subcommand: `render`

Renders one or more molecular maps to an image file.

### Arguments

| Argument | Description |
|----------|-------------|
| `input_file_path` | One or more input file paths (SBGN-ML or CellDesigner format) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file-path` | `-o` | Output file path (required) |
| `--renderer` | `-r` | Renderer to use: `svg-native`, `skia`, `cairo` (auto-detected if omitted) |
| `--format` | `-f` | Output format: `svg`, `pdf`, `png`, `jpeg`, `webp` (inferred from extension if omitted) |
| `--multi-pages` | `-m` | Render one map per page (for multi-input PDF) |
| `--to-top-left` | `-t` | Move elements to the top-left of the page |
| `--style-sheet-file-path` | `-s` | Style sheet file path (can be repeated for multiple style sheets) |

### Renderer/Format Compatibility

| Format | svg-native | skia | cairo |
|--------|-----------|------|-------|
| SVG | ✓ | ✓ | ✓ |
| PDF | ✗ | ✓ | ✓ |
| PNG | ✗ | ✓ | ✓ |
| JPEG | ✗ | ✓ | ✗ |
| WebP | ✗ | ✓ | ✗ |

**Note:** The `svg-native` renderer is always available and has no external dependencies. The `skia` and `cairo` renderers require optional dependencies to be installed.

## Examples

### Basic rendering

Render an SBGN-ML file to SVG:

```bash
momapy render my_map.sbgn -o output.svg
```

### Render to PDF

Render to PDF (requires skia or cairo renderer):

```bash
momapy render my_map.sbgn -o output.pdf
```

### Specify renderer explicitly

Force the use of a specific renderer:

```bash
momapy render my_map.sbgn -o output.pdf -r cairo
```

### Multiple input files

Render multiple maps into a single multi-page PDF:

```bash
momapy render map1.sbgn map2.sbgn map3.sbgn -o combined.pdf -m
```

### Apply style sheets

Apply one or more CSS style sheets to customize the appearance:

```bash
momapy render my_map.sbgn -o output.svg -s custom_styles.css
momapy render my_map.sbgn -o output.svg -s base.css -s overrides.css
```

### Adjust layout position

Move all elements to the top-left corner of the output:

```bash
momapy render my_map.sbgn -o output.svg -t
```

## Installation

The CLI is installed automatically when you install momapy:

```bash
pip install momapy
```

To use PDF, PNG, JPEG, or WebP output formats, install the optional rendering dependencies:

```bash
pip install momapy[skia]  # For skia renderer
pip install momapy[cairo]  # For cairo renderer
pip install momapy[all]    # For all renderers
```

## Getting Help

Display help information:

```bash
momapy --help
momapy render --help
```
