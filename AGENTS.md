# momapy — Agent Guide

**momapy** is a Python library for working with molecular maps (SBGN, CellDesigner). It reads/writes map files, computes geometry, applies CSS-like styling, and renders to SVG/PDF/PNG/JPEG/WebP.

- **Docs**: <https://adrienrougny.github.io/momapy/>
- **Issues**: <https://github.com/adrienrougny/momapy/issues>

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
├── cli.py            # CLI entry point (render subcommand)
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

### Frozen Dataclasses (Critical)

All map/layout/model elements are **frozen dataclasses**. Never mutate them directly.

```python
@dataclasses.dataclass(frozen=True, kw_only=True)
class MyElement(momapy.core.LayoutElement):
    position: momapy.geometry.Point
    width: float
    height: float
```

To modify, use the builder pattern:

```python
builder = momapy.builder.builder_from_object(obj)
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

- Simple elements (compartments, entity pools): singleton layout key → model element
- Child elements (state variables, subunits): singleton layout key → `(child_model, parent_model)` tuple
- Processes/reactions: **frozenset** key (process layout + participant arcs + participant targets) → process model. Each participant arc is also separately mapped as arc → `(participant_model, process_model)`.
- Modulations: **frozenset** key (modulation arc + source frozenset + target frozenset) → modulation model. Uses `_singleton_to_key` to resolve source/target frozensets.
- Each frozenset has exactly one **anchor** registered in `_singleton_to_key`.

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
