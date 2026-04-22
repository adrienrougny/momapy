# momapy — Agent Guide

**momapy** is a Python library for working with molecular maps (SBGN, CellDesigner). It reads/writes map files, computes geometry, applies CSS-like styling, and renders to SVG/PDF/PNG/JPEG/WebP.

- **Docs**: <https://adrienrougny.github.io/momapy/>
- **Issues**: <https://github.com/adrienrougny/momapy/issues>
- **API surface inventory**: `./API_REFERENCE.md` — module-by-module class/function signature reference. Load it when you need an orientation snapshot without reading every source file.

## Key Commands

```bash
# Install (all optional dependencies)
pip install -e ".[all]"
# or
uv sync --group dev

# Run tests
pytest tests/

# Run tests with coverage (minimum 70%)
pytest --cov=momapy --cov-report=html tests/

# CLI
momapy render map.sbgn -o output.svg
momapy render map.sbgn -o output.pdf -r cairo
momapy render map.sbgn -o output.svg -s style.css
momapy export map.sbgn -o output.sbgn
momapy export map.xml -o output.xml -c -s style.css
momapy visualize map.sbgn
momapy visualize map.xml -c -s style.css

# Docs
mkdocs serve
```

**Note**: Slow tests are marked `@pytest.mark.slow`.

## Project Structure

```
src/momapy/
├── core.py           # Base classes: Map, Model, Layout, LayoutElement, Arc, etc.
├── geometry.py       # Point, Bbox, Vector, path operations
├── drawing.py        # Drawing primitives: Path, Rectangle, Ellipse, Text, Group
├── builder.py        # Builder pattern for modifying frozen dataclasses
├── styling.py        # CSS-like stylesheet parsing and application
├── coloring.py       # Color definitions and management
├── positioning.py    # Layout positioning algorithms
├── cli.py            # CLI entry point (render, export subcommands)
├── utils.py          # SurjectionDict, pretty_print, helpers
├── meta/             # Generic shapes (Rectangle, Ellipse, Polygon, arcs)
├── sbgn/
│   ├── core.py       # Base SBGN classes
│   ├── pd.py         # SBGN Process Description glyphs (largest module)
│   ├── af.py         # SBGN Activity Flow glyphs
│   ├── utils.py      # SBGN utilities (tidying, fitting)
│   └── io/sbgnml/    # SBGN-ML I/O (see I/O Architecture below)
│       ├── reader.py, _reading_model.py, _reading_layout.py, ...
│       └── writer.py, _writing.py, _writing_classification.py
├── celldesigner/     # CellDesigner format support (same I/O module structure)
├── sbml/             # SBML support
├── rendering/        # Backends: svg_native, skia, cairo
├── io/core.py        # Reader/Writer base classes, ReaderResult, WriterResult
└── plugins/core.py   # Plugin registry with lazy loading
tests/
docs/
```

## Tech Stack

- **Python**: 3.10–3.14
- **Key deps**: numpy, lxml, frozendict, pyparsing, uharfbuzz
- **Optional**: skia-python, pycairo
- **Dev**: pytest, ruff, tox, mkdocs, git-cliff

## Code Conventions

### Formatting

Run `ruff format` on any file you edit before considering the change complete. The project follows ruff's default style; `ruff format src/ tests/` is the canonical way to normalise the tree.

### Imports

Absolute `from` imports are the default. The rules below are exhaustive — one style per case, no taste calls.

**1. Default — every `.py` file, including `__init__.py`.** Use `from momapy.x.y import Name` (absolute, no `as`). Never use relative imports (`from . import foo`, `from .sub import Name`): always spell the full `momapy.x.y` path.

```python
from momapy.core.elements import LayoutElement
from momapy.geometry import Point


@dataclasses.dataclass(frozen=True, kw_only=True)
class MyNode(LayoutElement):
    position: Point
```

**2. Re-exports in `__init__.py` only.** Use `from momapy.package.sub import Name as Name` — the `as Name` repeat is required. It is what Pyright, mypy, and Sphinx recognise as an intentional public re-export (PEP 484 implicit-re-export rule). List the re-exported names in `__all__`.

```python
# src/momapy/core/__init__.py
"""Core dataclasses for maps, models, and layouts."""

from momapy.core.layout import Node as Node
from momapy.core.layout import Arc as Arc

__all__ = ["Node", "Arc"]
```

**3. Name collisions — always rename.** When two modules export a name you both need, use `from momapy.x.y import Name as UnambiguousName`. No mixing of styles — the rename is the single form for the collision case, regardless of how often the name appears in the file.

```python
from momapy.meta.shapes import Rectangle as RectangleShape
from momapy.meta.nodes import Rectangle as RectangleNode
```

**4. Module-only imports.** `import momapy.x.y` (without `from`) is reserved for runtime dynamism or tooling use — `importlib`, `sys.modules` manipulation, entry-point dispatch. It is not part of the normal import style.

### Frozen Dataclasses (Critical)

All map/layout/model elements are **frozen dataclasses**. Never mutate them directly.

```python
from momapy.core.elements import LayoutElement
from momapy.geometry import Point


@dataclasses.dataclass(frozen=True, kw_only=True)
class MyElement(LayoutElement):
    position: Point
    width: float
    height: float
```

To modify, use the builder pattern:

```python
from momapy.builder import builder_from_object

builder = builder_from_object(obj)
builder.some_field = new_value
modified = builder.build()
```

### Naming

- Trailing underscore for reserved words: `id_`, `map_`, `type_`, `object_`
- Private attributes: `_name` prefix
- Classes: `PascalCase`; functions/variables: `snake_case`
- Enum members: `UPPER_CASE`
- Always use full words for variable names (e.g., `direction_x` not `dx`, `length` not `len`)

### Type Hints

Always use type hints. Use modern syntax (Python 3.10+):

- `list[T]` not `List[T]`
- `str | None` not `Optional[str]`
- `typing_extensions.Self` for methods returning `self`

### Docstrings

Google-style docstrings on all public APIs:

```python
def func(param1: str, param2: int = 0) -> list[str]:
    """Brief description.

    Args:
        param1: Description.
        param2: Description. Defaults to 0.

    Returns:
        Description.

    Raises:
        ValueError: When something is wrong.
    """
```

### Geometry

- Positions: `momapy.geometry.Point(x, y)`
- Bounding boxes: `momapy.geometry.Bbox(top_left, width, height)`
- Complex operations: analytical geometry (no shapely/bezier dependencies)

### Colors

- `momapy.coloring.Color` class
- Predefined: `momapy.coloring.black`, `momapy.coloring.white`, etc.

## Conventional Commits

Enforced via commitlint. Format: `<type>(<scope>): <subject>`

Types: `feat`, `fix`, `perf`, `refactor`, `doc`, `style`, `test`, `ci`, `chore`

Examples:

- `feat(sbgn.io): added support for AF compartment`
- `fix: activity is now a dataclass`
- `chore(sbgn.io.sbgnml): cleaned useless function`

## Architecture Overview

A **Map** has:

1. **Model** — semantic info (entities, processes, compartments)
2. **Layout** — visual info (positions, sizes, styles)
3. **Mapping** — links between model and layout elements

```python
from momapy.io.core import read

result = read("map.sbgn")
map_ = result.obj
model = map_.model
layout = map_.layout
# result.exceptions contains any parse errors
```

Every `LayoutElement` (frozen dataclass) must implement:

- `bbox()` → bounding box
- `drawing_elements()` → visual primitives
- `children()` → child elements
- `childless()` → copy without children

## I/O Architecture

Readers and writers for each format (SBGN-ML, CellDesigner) follow a shared architecture.

### Module structure

Each format lives in its own subpackage (e.g. `sbgn/io/sbgnml/`, `celldesigner/io/celldesigner/`) with:

- `reader.py` — main reader class (only the `read()` classmethod) + module-level `make_*` functions
- `_reading_model.py` — model-building `make_*` functions
- `_reading_layout.py` — layout-building `make_*` functions
- `_reading_classification.py` — maps XML keys to model/layout classes (reader-specific)
- `_reading_parsing.py` — XML traversal utilities
- `writer.py` — main writer class (only the `write()` classmethod) + module-level `make_*` functions
- `_writing.py` — XML construction helpers
- `_writing_classification.py` — maps model/layout classes to XML strings (writer-specific)

### Context objects

Both readers and writers use a **context dataclass** passed as the first argument to every function:

- **`ReadingContext`** (extends `momapy.io.utils.ReadingContext`): holds `model`, `layout`, `layout_model_mapping`, element ID lookups, classified XML element lists, annotations/notes state. Format-specific subclasses add fields (e.g. `sbgnml_glyph_id_to_sbgnml_arcs`).
- **`WritingContext`**: holds `map_`, `annotations`, `notes`, `ids`, flags.

There is no separate "parsed map" dataclass — classified element lists live directly in the context.

### Function conventions

- **Plain module-level functions**, not classmethods. The reader/writer class only keeps the `read()`/`write()` entry point.
- **`reading_context` / `writing_context`** as first parameter name (never `ctx`).
- **`make_*` naming** for both reading and writing functions. Reader functions create momapy objects; writer functions create XML elements. Both return the created object — the caller appends/registers.
- **None-early-return**: reader `make_*` functions check `reading_context.model is None` or `reading_context.layout is None` and return `None` early.
- **No staticmethod aliases** (e.g. no `_register_model_element = staticmethod(...)`). Call the function directly.
- **No module-level constant aliases** (e.g. no `_FOO = _writing._FOO`). Reference through the module.

### Reader traversal

Readers use an **interleaved** approach: for each XML element, create both the model element and layout element together, then wire up `layout_model_mapping`. This keeps natural pairing of model/layout children.

Processing order matters — compartments first (background), then entity pools, processes, modulations, etc.

### Writer traversal

Writers use a **model-first** approach: iterate model collections in dependency order (compartments → entity pools → processes → modulations), look up layout elements via `layout_model_mapping.get_mapping()`, and build XML from both model and layout data.

### layout_model_mapping

User-facing reference: see the "Layout-model mapping catalogue" section in the module docstrings of `momapy.sbgn.pd`, `momapy.sbgn.af`, and `momapy.celldesigner.model` (rendered on the corresponding API reference pages). The notes below cover the internals.

Every value in the mapping is a plain model element — there are no tuple values. Keys are either a singleton layout element or a frozenset of layout elements.

- Simple elements (compartments, entity pools, activities): singleton layout key → model element
- Child elements (state variables, units of information, subunits, modifications, terminals, reactants/products, logical operator inputs, tag/terminal references): singleton layout key → child model element
- Processes/reactions: **frozenset** key (process layout + participant arcs + participant targets) → process model
- Logical operators / boolean logic gates: **frozenset** key (operator layout + logic arcs + input targets) → operator model
- Modulations: **frozenset** key (modulation arc + source frozenset + target frozenset) → modulation model. Uses `_singleton_to_key` to resolve source/target frozensets.
- Tag/terminal with references: **frozenset** key (tag/terminal layout + reference arcs + referenced entity layouts) → tag/terminal model
- Each frozenset has exactly one **anchor** registered in `_singleton_to_key` (a `SurjectionDict`, so `inverse` gives frozenset → anchor in O(1))

`LayoutModelMapping.get_child_layout_elements(child_model_element, parent_model_element)` is the single helper used to look up the layout elements representing a child under a given parent. It computes the intersection of two sets:

- **S1** (layouts under the parent): children of each container layout mapped to the parent, plus members of each frozenset key mapped to the parent.
- **S2** (layouts for the child): singleton layouts mapped to the child, plus the anchors of any frozenset keys mapped to the child.

## Testing Patterns

```python
class TestSomething:
    def test_basic(self, sample_fixture):
        assert sample_fixture is not None

    @pytest.mark.slow
    def test_slow(self):
        pass
```

Common fixtures (from `conftest.py`): `sample_point`, `sample_bbox`, `sample_color`, `sample_layout`, `sample_node`, `sample_path`, `sample_sbgn_map`.

## CI/CD

- **Tests** (`.github/workflows/tests.yml`): ubuntu + windows + macos, Python 3.10/3.11/3.12/3.13/3.14
- **Release** (`.github/workflows/release.yml`): triggered by `v*.*.*` tags → test → build → publish to PyPI → generate changelog → GitHub release
- **Docs** (`.github/workflows/docs.yml`): deploy to GitHub Pages after release

## ID Assignment Patterns

### SBGN-ML

All elements follow a consistent pattern: model `id_` = `f"{xml_id}_model"`, layout `id_` = `xml_id`.
Both `xml_id_to_model_element` and `xml_id_to_layout_element` are keyed by the raw `xml_id`.

| Element Type | Model `id_` | Layout `id_` | Registered | Notes |
|---|---|---|---|---|
| Compartment | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| EntityPool / Subunit | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| Activity | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| StateVariable | `f"{glyph_id}_model"` | `glyph_id` | yes | Frozen child |
| UnitOfInformation | `f"{glyph_id}_model"` | `glyph_id` | yes | Frozen child |
| Submap | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| Terminal / Tag | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| TerminalRef / TagRef | `f"{arc_id}_model"` | `arc_id` | yes | Frozen child |
| StoichiometricProcess | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| Reactant | `f"{arc_id}_model"` | `arc_id` | yes | Frozen child |
| Product | `f"{arc_id}_model"` | `arc_id` | yes | Frozen child |
| LogicalOperator | `f"{glyph_id}_model"` | `glyph_id` | yes | |
| LogicalOperatorInput | `f"{arc_id}_model"` | `arc_id` | yes | Frozen child |
| Modulation | `f"{arc_id}_model"` | `arc_id` | yes | |
| Phenotype | `f"{glyph_id}_model"` | `glyph_id` | yes | In model.processes |

Map/model/layout IDs from `<map id="...">`: `map_.id_` = map_id, `model.id_` = `f"{map_id}_model"`, `layout.id_` = `f"{map_id}_layout"`. Only set for SBGN-ML 0.3 (0.2 has no map id → UUID defaults).

### CellDesigner

More complex than SBGN: model and layout often use different XML ID sources (e.g., `<species id>` vs `<speciesAlias id>`). Some elements have no XML ID and use SBML `metaid`, composite IDs, or auto-generated UUIDs.

**ID provenance key**:
- `sbml:X` — from an SBML element attribute (e.g., `<species id="s1">`, `<modifierSpeciesReference metaid="MSR0">`)
- `cd:X` — from a CellDesigner extension element attribute (e.g., `<speciesAlias id="sa1">`)
- `composite` — synthetic ID built from parent + child XML IDs
- `auto` — auto-generated UUID from the builder

| Element Type | Model `id_` | Source | Layout `id_` | Source | Registered | Notes |
|---|---|---|---|---|---|---|
| Compartment | `compartment_id` | sbml:`compartment/@id` | `alias_id` | cd:`compartmentAlias/@id` | yes | `metaid` also stored |
| Species Template | `template_id` | cd:`proteinReference/@id` etc. | no layout | — | yes | |
| Species | `species_id` or `f"{species_id}_active"` | sbml:`species/@id` | `alias_id` | cd:`speciesAlias/@id` | yes | Dual model reg.; active species get `_active` suffix |
| ModificationResidue | `f"{template_id}_{residue_id}"` | composite | no layout | — | yes | Global uniqueness via parent |
| Region | `f"{template_id}_{region_id}"` | composite | no layout | — | yes | Global uniqueness via parent |
| Modification | `f"{species_id}_{residue_id}"` | composite | `f"{species_id}_{residue_id}_layout"` | composite | no | Deterministic from species + residue |
| StructuralState | `f"{species_id}_{value}"` | composite | `f"{species_id}_{value}_layout"` | composite | no | Deterministic from species + value |
| Reactant (base/link) | `metaid` or `f"{reaction_id}_{species_id}"` | sbml:`speciesReference/@metaid` or composite | `f"{model_id}_layout"` | derived from model id | yes | metaid preferred; layout only for link reactants and some base |
| Product (base/link) | `metaid` or `f"{reaction_id}_{species_id}"` | sbml:`speciesReference/@metaid` or composite | `f"{model_id}_layout"` | derived from model id | yes | metaid preferred; layout only for link products and some base |
| Modulator | `metaid` | sbml:`modifierSpeciesReference/@metaid` | `f"{metaid}_layout"` | derived from metaid | yes | metaid always present |
| BooleanGate | `f"{reaction_id}_gate_{sorted_aliases}"` | composite | `f"{...}_layout"` | composite | model only | Deterministic from reaction + sorted aliases |
| BooleanGateInput / LogicArcLayout | `f"{gate_id}_input_{input_alias}"` | composite | `f"{gate_id}_arc_{input_alias}"` | composite | no | Frozen child of gate |
| Reaction | `reaction_id` | sbml:`reaction/@id` | `f"{reaction_id}_layout"` | derived from sbml | yes | No reaction alias in CD |
| Modulation | `reaction_id` | sbml:`reaction/@id` | `f"{reaction_id}_layout"` | derived from sbml | yes | Encoded as fake reactions |

**Notes**:
- **Dual registration**: Species model is registered in `xml_id_to_model_element` under both `species_id` AND `species_alias_id` (CellDesigner reactions reference species by alias ID for cross-ref resolution)
- **`_layout` suffix**: Used when model and layout share the same XML ID source (reactions, modulations, modulators with metaid). No suffix needed when they come from different XML elements (species vs alias, compartment vs alias)
- **metaid**: SBML `metaid` attribute is preferred for Reactants, Products, and Modulators. Falls back to composite ID or UUID when absent
- **Composite IDs**: `f"{parent_id}_{child_id}"` for ModificationResidue and Region (child IDs are only unique within a parent template)

## Plans

Write implementation plans to `./plans/` as markdown files. Use descriptive filenames (e.g., `active_border_child_nodes.md`). Also write design debates to `./debates/`.

## DO / DON'T

**DO:**

- Use frozen dataclasses for model/layout elements
- Use builder pattern for modifications
- Add type hints and Google-style docstrings everywhere
- Mark slow tests with `@pytest.mark.slow`
- Use conventional commits
- Break the API when needed — we are still in a 0.X version

**DON'T:**

- Mutate frozen dataclasses directly
- Skip type hints or docstrings
- Bypass test coverage (70% minimum)
- Add unnecessary complexity or premature abstractions
- Use dangerouslyDisableSandbox (Claude code)
