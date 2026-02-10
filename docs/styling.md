# Styling Guide

## Overview

momapy supports CSS-like stylesheets for customizing the appearance of molecular maps. Stylesheets allow you to control colors, fonts, strokes, and other visual properties of map elements without modifying the underlying map data.

Stylesheets are applied during rendering and can be used via the command line (`-s` flag) or the Python API.

## Basic Syntax

Stylesheets follow a CSS-like syntax with rules, selectors, and declaration blocks:

```css
MacromoleculeLayout {
    fill: royalblue;
    stroke: white;
    stroke-width: 2.0;
}
```

A rule consists of:

- **Selector**: The element(s) to style (e.g., `MacromoleculeLayout`)
- **Declaration block**: Properties and values inside `{ }`
- **Properties**: Visual attributes (e.g., `fill`, `stroke-width`)
- **Values**: The setting for each property (e.g., `royalblue`, `2.0`)

## Selectors

### Type Selector

Matches elements by their exact class name:

```css
MacromoleculeLayout {
    fill: lightblue;
}
```

This matches only `MacromoleculeLayout` elements, not subclasses.

### Class Selector

Matches a class and all its subclasses (prefix with dot):

```css
.Shape {
    stroke-width: 2.0;
}
```

This matches `Shape` and any subclass like `Rectangle`, `Ellipse`, etc.

### ID Selector

Matches an element by its `id_` attribute:

```css
#my_protein {
    fill: red;
}
```

### Child Selector

Matches direct children only (use `>`):

```css
StateVariableLayout > TextLayout {
    font-size: 8.0;
}
```

### Descendant Selector

Matches elements at any depth:

```css
Group TextLayout {
    fill: white;
}
```

### Or Selector

Matches any of multiple selectors (comma-separated):

```css
MacromoleculeLayout, SimpleChemicalLayout {
    stroke: black;
}
```

## Value Types

### Numbers

- **Floats**: `2.0`, `10.5`
- **Integers**: `42`

### Strings

Quoted strings for font names and other text values:

```css
font-family: "DejaVu Sans";
```

### Colors

Color names or hex values:

```css
fill: royalblue;
stroke: #FF5733;
```

### Special Values

- **`none`**: No value (e.g., `fill: none;`)
- **`unset`**: Reset to default/inherited value

### Lists

Comma-separated lists:

```css
stroke-dasharray: 5, 5;
```

### Filters

Drop shadow effect:

```css
filter: drop-shadow(2.0, 2.0, 3.0, 0.5, gray);
```

Parameters: `drop-shadow(dx, dy, std_dev, opacity, color)`

## Common Properties

### Drawing Properties

| Property | Description | Example |
|----------|-------------|---------|
| `fill` | Fill color | `fill: royalblue;` |
| `stroke` | Stroke/border color | `stroke: black;` |
| `stroke-width` | Stroke thickness | `stroke-width: 2.0;` |
| `stroke-dasharray` | Dash pattern | `stroke-dasharray: 5, 5;` |
| `opacity` | Opacity (0.0-1.0) | `opacity: 0.8;` |
| `filter` | Visual effects | `filter: drop-shadow(2, 2, 3, 0.5, gray);` |

### Text Properties

| Property | Description | Example |
|----------|-------------|---------|
| `font-family` | Font name | `font-family: "DejaVu Sans";` |
| `font-size` | Font size | `font-size: 14.0;` |
| `fill` | Text color | `fill: white;` |
| `font-style` | Font style | `font-style: italic;` |
| `font-weight` | Font weight | `font-weight: bold;` |

### Shape Properties

| Property | Description | Example |
|----------|-------------|---------|
| `width` | Element width | `width: 100.0;` |
| `height` | Element height | `height: 60.0;` |
| `rounded-corners` | Corner radius | `rounded-corners: 5.0;` |
| `cut-corners` | Cut corner size | `cut-corners: 10.0;` |

**Note**: Some node and arc classes have specific attributes that define their shape geometry. For example, `angle` and `offset` are parameters used by certain shape types (like hexagons with specific corner angles) and are not rotation angles or position offsets. Refer to the specific node or arc class implementation to see which shape-specific properties are available.

### Connector Properties

| Property | Description | Example |
|----------|-------------|---------|
| `left-connector-length` | Left connector size | `left-connector-length: 10.0;` |
| `left-connector-stroke` | Left connector color | `left-connector-stroke: gray;` |
| `right-connector-length` | Right connector size | `right-connector-length: 10.0;` |
| `right-connector-stroke` | Right connector color | `right-connector-stroke: gray;` |

### Arrowhead Properties

| Property | Description | Example |
|----------|-------------|---------|
| `arrowhead-fill` | Arrowhead fill color | `arrowhead-fill: black;` |
| `arrowhead-stroke` | Arrowhead stroke color | `arrowhead-stroke: gray;` |
| `arrowhead-stroke-width` | Arrowhead stroke width | `arrowhead-stroke-width: 1.5;` |

Note: Not all arcs have arrowheads. For example, `ConsumptionLayout` is rendered as a simple line (polyline) without an arrowhead.

### Path Properties

| Property | Description | Example |
|----------|-------------|---------|
| `path-stroke` | Path color | `path-stroke: gray;` |
| `path-stroke-width` | Path thickness | `path-stroke-width: 1.5;` |
| `end-shorten` | Shorten path at end | `end-shorten: 1.0;` |

### Group Properties

Prefix with `group-` to style child elements collectively:

```css
MacromoleculeLayout {
    group-stroke: black;
    group-fill: lightgray;
}
```

## Imports

Stylesheets can import other stylesheets using the `@import` rule:

```css
@import "base.css";
@import "overrides.css";

MacromoleculeLayout {
    fill: blue;
}
```

Imports are processed in order, with later rules overriding earlier ones.

## Usage

### Command Line

Apply a stylesheet when rendering:

```bash
momapy render map.sbgn -o output.svg -s my_style.css
```

Apply multiple stylesheets (applied in order):

```bash
momapy render map.sbgn -o output.svg -s base.css -s overrides.css
```

### Python API

Load from file:

```python
from momapy.styling import StyleSheet

style_sheet = StyleSheet.from_file("my_style.css")
```

Load from string:

```python
style_sheet = StyleSheet.from_string("""
MacromoleculeLayout {
    fill: blue;
}
""")
```

Apply to a layout:

```python
from momapy.styling import apply_style_sheet

apply_style_sheet(map_.layout, style_sheet)
```

Or apply during rendering:

```python
from momapy.rendering.core import render_map

render_map(map_, "output.svg", style_sheet=style_sheet)
```

## Complete Example

Here's a custom stylesheet for some layout elements of SBGN PD:

```css
/* Import a base stylesheet */
@import "my_base_stylesheet.css";

/* Style state variables */
StateVariableLayout {
    fill: royalblue;
    stroke: white;
    stroke-width: 1.5;
}

/* Style text inside state variables */
StateVariableLayout > TextLayout {
    font-size: 7.0;
    fill: white;
}

/* Style macromolecules */
MacromoleculeLayout {
    fill: royalblue;
    stroke: white;
    stroke-width: 2.0;
}

MacromoleculeLayout > TextLayout {
    font-size: 14.0;
    fill: white;
}

/* Style simple chemicals */
SimpleChemicalLayout {
    fill: gold;
    stroke: white;
    stroke-width: 2.0;
}

SimpleChemicalLayout > TextLayout {
    font-size: 10.0;
    fill: black;
}

/* Style processes with connectors */
GenericProcessLayout {
    fill: gray;
    stroke: white;
    right-connector-stroke: gray;
    right-connector-length: 10.0;
    left-connector-stroke: gray;
    left-connector-length: 10.0;
}

/* Style consumption arc (polyline, no arrowhead) */
ConsumptionLayout {
    path-stroke: gray;
    path-stroke-width: 1.5;
    end-shorten: 1.0;
}

/* Style production arc */
ProductionLayout {
    arrowhead-fill: gray;
    arrowhead-stroke: gray;
    path-stroke: gray;
    path-stroke-width: 1.5;
    end-shorten: 1.0;
}
```
