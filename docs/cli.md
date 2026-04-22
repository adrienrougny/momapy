# CLI Reference

## Overview

The `momapy` command-line interface (CLI) allows you to work with molecular maps directly from the command line without writing Python code. It supports SBGN-ML and CellDesigner map formats.

Available subcommands:

- **`render`** — Render maps to image formats (SVG, PDF, PNG, JPEG, WebP)
- **`export`** — Export maps back to their original format (useful for roundtrip testing)
- **`info`** — Print a summary of a map file's contents
- **`list`** — List available readers, writers, renderers, colors, styles, or stylable attributes
- **`tidy`** — Apply layout tidying operations (fit nodes, snap arcs, etc.)
- **`style`** — Bake CSS stylesheets into map data and output the styled map
- **`visualize`** — Open an interactive viewer in the default web browser

## Synopsis

```bash
momapy render <input_file_path>... -o <output_file_path> [options]
momapy export <input_file_path> -o <output_file_path> [options]
momapy info <input_file_path> [options]
momapy list {readers,writers,renderers,colors,styles,attributes}
momapy tidy <operation> [<input_file_path>] [options]
momapy style [<input_file_path>] [options]
momapy visualize <input_file_path> [options]
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
| `--to-top-left` | `-l` | Move elements to the top-left of the page |
| `--tidy` | `-t` | Tidy the map (reroute arcs, fit labels, etc.) |
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
momapy render my_map.sbgn -o output.svg -l
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

## Subcommand: `export`

Reads a map and writes it back in the same format. This is useful for roundtrip testing (read with the reader, write with the writer) and for applying transformations like tidying or styling before re-exporting.

### Arguments

| Argument | Description |
|----------|-------------|
| `input_file_path` | Input file path (SBGN-ML or CellDesigner format) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file-path` | `-o` | Output file path (default: stdout) |
| `--tidy` | `-t` | Tidy the map (reroute arcs, fit labels, etc.) |
| `--to-top-left` | `-l` | Move elements to the top-left of the page |
| `--style-sheet-file-path` | `-s` | Style sheet file path (can be repeated for multiple style sheets) |

The writer is inferred automatically from the map type: SBGN maps are exported using the `sbgnml` writer, CellDesigner maps using the `celldesigner` writer.

If no output file is specified, the result is written to standard output.

### Examples

#### Export to stdout

```bash
momapy export my_map.sbgn
```

#### Basic roundtrip

Export an SBGN-ML file:

```bash
momapy export my_map.sbgn -o output.sbgn
```

Export a CellDesigner file:

```bash
momapy export my_map.xml -o output.xml
```

#### Export with tidy

Tidy the map before exporting (reroute arcs, fit labels, etc.):

```bash
momapy export my_map.sbgn -o output.sbgn -t
```

#### Apply style sheets

Apply a stylesheet before exporting:

```bash
momapy export my_map.sbgn -o output.sbgn -s custom_styles.css
momapy export my_map.sbgn -o output.sbgn -s base.css -s overrides.css
```

## Subcommand: `info`

Prints a summary of a map file's contents, including the map type, model element counts, and layout dimensions.

### Arguments

| Argument | Description |
|----------|-------------|
| `input_file_path` | Input file path (SBGN-ML or CellDesigner format) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file-path` | `-o` | Output file path (default: stdout) |
| `--format` | `-f` | Output format: `text` (default) or `json` |

### Examples

#### Inspect an SBGN-ML file

```bash
momapy info my_map.sbgn
```

Output:

```
File:      my_map.sbgn
Map type:  SBGN Process Description

Model:
  compartments:             0
  entity pools:             28
  processes:                10
  modulations:              10
  logical operators:        0
  equivalence operators:    0
  submaps:                  0
  tags:                     0

Layout:
  dimensions:               1170.0 x 560.0
  elements:                 122
```

#### JSON output

```bash
momapy info my_map.sbgn --format json
```

Output:

```json
{
  "map_type": "SBGN Process Description",
  "model": {
    "compartments": 0,
    "entity_pools": 28,
    "processes": 10,
    "modulations": 10,
    "logical_operators": 0,
    "equivalence_operators": 0,
    "submaps": 0,
    "tags": 0
  },
  "layout": {
    "width": 1170.0,
    "height": 560.0,
    "elements": 122
  },
  "file": "my_map.sbgn"
}
```

#### Inspect a CellDesigner file

```bash
momapy info my_map.xml
```

## Subcommand: `list`

Lists plugins, named colors, built-in style presets, or stylable attributes of a layout element class.

### Arguments

| Argument | Description |
|----------|-------------|
| `readers` | List available map readers |
| `writers` | List available map writers |
| `renderers` | List available renderers (with supported output formats) |
| `colors` | List all named colors (displayed in their own color) |
| `styles` | List built-in style presets |
| `attributes <class_path>` | List stylable attributes of a layout element class |

### Examples

#### List available readers

```bash
momapy list readers
```

Output:

```
celldesigner
pickle
sbgnml
sbgnml-0.2
sbgnml-0.3
sbml
```

#### List available writers

```bash
momapy list writers
```

Output:

```
celldesigner
pickle
sbgnml
sbgnml-0.3
```

#### List available renderers

```bash
momapy list renderers
```

Output:

```
cairo (formats: pdf, svg, png, ps)
skia (formats: pdf, svg, png, jpeg, webp)
svg-native (formats: svg)
svg-native-compat (formats: svg)
```

If a renderer's dependencies are not installed, it shows `(not installed)` instead of formats.

#### List named colors

```bash
momapy list colors
```

Each color name is printed in its own color. Useful for picking values for `fill`, `stroke`, and similar properties in stylesheets.

#### List built-in style presets

```bash
momapy list styles
```

Output:

```
cs_black_and_white       Black and white colorscheme
cs_default               Default colorscheme
fs_shadows               Drop shadows
newt                     Newt style
sbgned                   SBGN-ED style
```

Preset names can be passed to `momapy style -p` or `momapy render`/`momapy export` via `--preset`.

#### List stylable attributes of a class

```bash
momapy list attributes momapy.sbgn.pd:MacromoleculeLayout
```

Lists every attribute that can be targeted in a stylesheet for the given class. Pass `-p` / `--presentation-only` to restrict the output to visual presentation attributes (fill, stroke, font, etc.).

```bash
momapy list attributes momapy.sbgn.pd:MacromoleculeLayout --presentation-only
```

## Subcommand: `tidy`

Applies layout tidying operations to a map and outputs the result. Use a specific operation sub-command or `all` to run the full pipeline.

### Synopsis

```bash
momapy tidy <operation> [<input_file_path>] [options]
```

### Operations

| Operation | Description |
|-----------|-------------|
| `all` | Apply all tidying operations in sequence |
| `fit-species` | Resize species nodes to fit their labels (CellDesigner only) |
| `fit-epns` | Resize entity pool nodes to fit their labels (SBGN only) |
| `fit-auxiliary` | Position and resize auxiliary elements (modifications/state variables/units of information) |
| `fit-complexes` | Resize complexes to fit their subunits |
| `fit-compartments` | Resize compartments to fit their content |
| `fit-submaps` | Resize submaps to fit their terminals (SBGN only) |
| `fit-layout` | Resize the overall layout to fit all elements |
| `snap-arcs` | Snap arc endpoints to node borders |
| `straighten-arcs` | Straighten near-horizontal and near-vertical arc segments (CellDesigner only) |

### Options

All operations accept:

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file-path` | `-o` | Output file path (default: stdout) |

The `all`, `fit-species`, `fit-epns`, `fit-auxiliary`, `fit-complexes`, `fit-compartments`, `fit-submaps`, and `fit-layout` operations also accept:

| Option | Description |
|--------|-------------|
| `--xsep <float>` | Horizontal padding (default: depends on operation and map type) |
| `--ysep <float>` | Vertical padding (default: depends on operation and map type) |

The `all` and `straighten-arcs` operations also accept:

| Option | Description |
|--------|-------------|
| `--angle-tolerance <float>` | Angle tolerance in degrees for straightening (default: 5.0) |

### Examples

#### Apply all tidying operations

```bash
momapy tidy all my_map.sbgn -o tidy_map.sbgn
```

#### Fit entity pool nodes to their labels

```bash
momapy tidy fit-epns my_map.sbgn -o tidy_map.sbgn
```

#### Snap arc endpoints to node borders with custom padding

```bash
momapy tidy snap-arcs my_map.sbgn -o tidy_map.sbgn --xsep 5.0 --ysep 5.0
```

#### Read from stdin and write to stdout (pipeline)

```bash
cat my_map.sbgn | momapy tidy all > tidy_map.sbgn
```

## Subcommand: `style`

Applies CSS stylesheets (and/or built-in presets) to a map, baking the styles into the map data, and outputs the result. Multiple `-s` and `-p` flags can be interleaved; stylesheets are merged left-to-right (later rules override earlier ones).

### Arguments

| Argument | Description |
|----------|-------------|
| `input_file_path` | Input file path (reads from stdin if omitted) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output-file-path` | `-o` | Output file path (default: stdout) |
| `--style-sheet-file-path` | `-s` | Custom CSS file path (repeatable) |
| `--preset` | `-p` | Built-in preset name (repeatable); see `momapy list styles` |

### Examples

#### Apply a custom stylesheet

```bash
momapy style my_map.sbgn -s my_style.css -o styled_map.sbgn
```

#### Apply a built-in preset

```bash
momapy style my_map.sbgn -p sbgned -o styled_map.sbgn
```

#### Combine a preset with a custom override

```bash
momapy style my_map.sbgn -p cs_default -s overrides.css -o styled_map.sbgn
```

#### Read from stdin

```bash
cat my_map.sbgn | momapy style -p newt > styled_map.sbgn
```

## Subcommand: `visualize`

Opens an interactive viewer for a molecular map in the default web browser. The viewer is a self-contained HTML page with the map rendered as inline SVG, featuring:

- **Pan and zoom** — click and drag to pan, scroll to zoom, double-click to reset
- **Hover tooltips** — hover over any element to see its type, layout ID, model ID, and label
- **Click to inspect** — click an element to pin its info in a bottom panel with selectable/copyable text
- **Search** — search by label or ID; matching elements and their descendants stay visible while everything else is dimmed. Press Enter to pan to the first match, Escape to clear.
- **Keyboard shortcuts** — Ctrl+F / Cmd+F to focus the search bar

### Arguments

| Argument | Description |
|----------|-------------|
| `input_file_path` | Input file path (SBGN-ML or CellDesigner format) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--tidy` | `-t` | Tidy the map (reroute arcs, fit labels, etc.) |
| `--to-top-left` | `-l` | Move elements to the top-left of the page |
| `--style-sheet-file-path` | `-s` | Style sheet file path (can be repeated for multiple style sheets) |

### Examples

#### Basic visualization

```bash
momapy visualize my_map.sbgn
```

#### Visualize with tidy and style sheet

```bash
momapy visualize my_map.xml -t -s custom_styles.css
```

## Getting Help

Display help information:

```bash
momapy --help
momapy render --help
momapy export --help
momapy info --help
momapy list --help
momapy tidy --help
momapy style --help
momapy visualize --help
```
