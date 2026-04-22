---
name: momapy
description: Build, read, write, modify, or render SBGN (Process Description / Activity Flow) and CellDesigner molecular maps with the momapy Python library. Trigger when a project imports `momapy`, when the user asks about the momapy API (Map / Model / Layout / `LayoutModelMapping`, frozen dataclasses, the builder pattern, `read()` / `write()`, rendering to SVG/PDF/PNG), or when working with `.sbgn`, `.sbgnml`, `.xml` (CellDesigner) files in a momapy context.
---

# momapy

`momapy` is a Python library for working with **molecular maps**: SBGN (PD and AF) and CellDesigner. It separates a map's **semantics** (what the diagram represents) from its **visual layout** (how it is drawn) and provides readers, writers, renderers, and CSS-like styling.

This skill captures the rules and recipes you need to write correct momapy code. **Read `momapy`'s installed source** (or its docs at <https://adrienrougny.github.io/momapy/>) for exact signatures — class hierarchies are large.

---

## Mental model

A `momapy.core.Map` has three fields:

- **`model`** — semantic content. Entity pools, processes, modulations, compartments, … (subclasses of `ModelElement`).
- **`layout`** — visual content. Positions, sizes, shapes, arcs, styles (subclasses of `LayoutElement`).
- **`layout_model_mapping`** — a `LayoutModelMapping` that maps each layout element (or frozenset of layout elements, for processes/modulations/operators) to the model element it represents.

You can have several layout elements representing the same model element (the same molecule drawn twice). The mapping is what tells you "this glyph means *that* molecule".

```python
from momapy.io import read

result = read("map.sbgn")
map_ = result.obj
print(map_.model)              # SBGNPDModel / SBGNAFModel / CellDesignerModel
print(map_.layout)             # the visual tree
print(map_.layout_model_mapping)  # bidirectional links
print(result.exceptions)       # any non-fatal parse issues
```

---

## CRITICAL: frozen dataclasses and the builder pattern

**Every** model element, layout element, mapping, and `Map` is a **frozen dataclass**. You cannot assign to its fields. Trying to mutate one will raise `dataclasses.FrozenInstanceError`.

To "modify" an object, wrap it in a builder, mutate the builder, then build a new immutable object:

```python
from momapy.builder import builder_from_object

builder = builder_from_object(map_)            # returns a MapBuilder
builder.layout.fill = momapy.coloring.lightgray
new_map = builder.build()                       # frozen Map again
```

Rules:

- Never write `obj.field = value` on a frozen dataclass — always go through a builder.
- `builder_from_object()` recursively wraps every nested frozen dataclass into a builder, so you can mutate deeply nested fields directly on the returned builder.
- `builder.build()` recursively re-freezes everything.
- For collections of children: `frozenset` and `tuple` fields become `set` and `list` in the builder; mutate them in place.
- To create a fresh element, use `new_builder_object(SomeClass, …)` from `momapy.builder`, set fields, then `.build()`.

```python
from momapy.builder import new_builder_object
from momapy.sbgn.pd import Macromolecule

mac_builder = new_builder_object(Macromolecule, label="ATP")
mac = mac_builder.build()
```

If you ever feel tempted to do `object.__setattr__(obj, "field", value)` to bypass the freeze — stop. You will silently break equality, hashing, and the cached id maps. Use a builder.

---

## Reading a map

```python
from momapy.io import read

# Format auto-detected from file extension; pass reader="sbgnml" / "celldesigner" / "pickle" to force.
result = read("map.sbgn")

map_ = result.obj                                  # Map
annotations = result.element_to_annotations        # dict[MapElement, list[Annotation]]
notes = result.element_to_notes                    # dict[MapElement, str]
xml_id_lookup = result.id_to_element               # dict[str, MapElement]
```

To list available readers / writers:

```python
from momapy.io import list_readers, list_writers
list_readers()   # ['sbgnml', 'celldesigner', 'pickle', ...]
list_writers()
```

Reader-specific options can be passed as kwargs to `read()` (e.g. `with_annotations=False`, `with_notes=False`, `return_type="map"`). See each reader's `read()` for the full signature.

---

## Writing a map

```python
from momapy.io import write

write(map_, "out.sbgn", writer="sbgnml")
write(map_, "out.xml", writer="celldesigner")
write(map_, "out.pkl", writer="pickle")
```

The writer is **not** auto-detected from the extension — pass `writer=` explicitly.

---

## Rendering

Three rendering backends are available:

| Backend | Formats | Install |
|---|---|---|
| `svg_native` | svg | always available |
| `cairo` | pdf, svg, png, ps | `pip install momapy[cairo]` |
| `skia` | pdf, svg, png, jpeg, webp | `pip install momapy[skia]` |

```python
from momapy.rendering import render_map
from momapy.styling import StyleSheet

render_map(map_, "out.svg")                       # svg_native, auto-detected from extension
render_map(map_, "out.pdf", renderer="cairo")
render_map(map_, "out.png", renderer="skia")

style = StyleSheet.from_file("style.css")
render_map(map_, "out.svg", style_sheet=style, to_top_left=True)
```

For multi-page output or rendering a list of maps, use `render_maps([...], ...)`.

---

## Modifying a map

The full pattern: read → builder → mutate → build → write.

```python
from momapy.builder import builder_from_object
from momapy.io import read, write
from momapy import coloring

result = read("map.sbgn")
map_builder = builder_from_object(result.obj)

# Tweak every macromolecule layout's fill colour
from momapy.sbgn.pd import MacromoleculeLayout
for layout_element in map_builder.layout.descendants():
    if isinstance(layout_element, MacromoleculeLayout):
        layout_element.fill = coloring.lightyellow

new_map = map_builder.build()
write(new_map, "tinted.sbgn", writer="sbgnml")
```

`descendants()` and `flattened()` walk the tree for you — prefer them over hand-written recursion.

### Adding a new element

1. Build the model element (`new_builder_object(<ModelClass>, …).build()`).
2. Add it to the appropriate model collection on the builder (`map_builder.model.entity_pools.add(...)`).
3. Build the layout element similarly and add it to a parent layout's `elements`.
4. Register the link in the mapping: `map_builder.layout_model_mapping.add_mapping(layout_el, model_el)`.
5. For composite keys (processes, modulations, logical operators, tags-with-references) the key is a `frozenset` — see the **layout_model_mapping** section of the project's `CLAUDE.md` for the exact convention. Pick an `anchor` so `_singleton_to_key` can resolve back from the anchor element.

---

## Styling

CSS-like stylesheets, applied either before rendering (via `style_sheet=`) or directly to a layout:

```python
from momapy.styling import StyleSheet, apply_style_sheet

style = StyleSheet.from_string("""
MacromoleculeLayout { fill: lightblue; stroke-width: 2; }
""")
apply_style_sheet(map_, style)
```

Predefined stylesheets live in `momapy.sbgn.styling`: `cs_default`, `cs_black_and_white`, `sbgned`, `newt`, `fs_shadows`. Combine with `|` or `combine_style_sheets([...])`.

---

## CLI

The `momapy` CLI wraps the most common operations:

```bash
momapy render map.sbgn -o out.svg
momapy render map.sbgn -o out.pdf -r cairo -s style.css
momapy export map.sbgn -o out.xml          # convert SBGN-ML → CellDesigner
momapy visualize map.sbgn                  # GLFW window
momapy tidy map.sbgn -o tidied.sbgn
momapy list readers                        # also: writers, renderers, styles
momapy info                                # version + capabilities
```

---

## Where to look

When you need an exact signature, prefer reading the source over guessing — class hierarchies are large and many fields are format-specific.

| You need… | Look in… |
|---|---|
| Base classes (`Map`, `Model`, `Layout`, `Node`, `Arc`) | `momapy/core/` |
| Geometry (`Point`, `Bbox`, transformations) | `momapy/geometry.py` |
| Drawing primitives | `momapy/drawing.py` |
| Builder utilities | `momapy/builder.py` |
| SBGN PD model + layout classes | `momapy/sbgn/pd/` |
| SBGN AF model + layout classes | `momapy/sbgn/af/` |
| CellDesigner model + layout | `momapy/celldesigner/` |
| SBGN-ML reader/writer | `momapy/sbgn/io/sbgnml/` |
| Generic shapes / nodes / arcs | `momapy/meta/` |
| Predefined styles | `momapy/sbgn/styling/` |
| SBGN tidying helpers | `momapy/sbgn/utils.py` (`tidy`, `sbgned_tidy`, `newt_tidy`) |

An `API_REFERENCE.md` ships alongside this skill (and is symlinked at the repo root for contributors working inside the `momapy` source tree). It is a curated module-by-module signature inventory — read it first for orientation.

---

## Common pitfalls

- **Mutating a frozen dataclass.** Will raise `FrozenInstanceError`. Use `builder_from_object` / `new_builder_object`.
- **Forgetting to register a layout element in `layout_model_mapping`.** The element will render but won't round-trip through writers, won't be looked up by `map_.get_mapping(...)`, and won't survive serialisation cleanly.
- **Auto-detecting the writer.** `write()` does *not* infer from the file extension — pass `writer="sbgnml"` (or similar) explicitly.
- **Mixing model and layout responsibilities.** Semantic data (label, type, references) belongs on the model element. Visual data (position, size, fill, stroke, font) belongs on the layout element. Don't put a colour on a `Macromolecule`; put it on the `MacromoleculeLayout`.
- **Reaching past `result.obj`.** `read()` returns a `ReaderResult` — the `Map` is on `.obj`. `result.exceptions` carries non-fatal parse errors worth checking.
- **Using `==` on layout trees you expect to be "the same shape".** Equality is structural and includes IDs / nested fields; for shape-only comparison use `LayoutElement.equals(other, flattened=True, unordered=True)`.
- **Picking the wrong renderer for the format.** `svg_native` only does SVG; PDF/PNG/JPEG/WebP need `cairo` or `skia`. Check `Renderer.supported_formats` or use `momapy list renderers`.

---

## Conventions when generating momapy code

Match the project's own style so your output drops into the codebase cleanly:

- Absolute imports only: `from momapy.sbgn.pd import Macromolecule` — never relative.
- Rename on collision: `from momapy.meta.shapes import Rectangle as RectangleShape`.
- `kw_only=True, frozen=True` on every dataclass that subclasses a momapy element.
- Trailing underscore for reserved-word attributes: `id_`, `map_`, `type_`.
- Full names for variables — `direction_x`, not `dx`; `length`, not `len`.
- Type hints on everything; modern syntax (`list[T]`, `str | None`, `typing_extensions.Self`).
- Google-style docstrings on public functions and classes.
- Run `ruff format` on any file you write.
