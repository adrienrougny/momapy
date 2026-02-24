# momapy — Agent Guide

**momapy** is a Python library for working with molecular maps (SBGN, CellDesigner). It reads/writes map files, computes geometry, applies CSS-like styling, and renders to SVG/PDF/PNG/JPEG/WebP.

- **Docs**: https://adrienrougny.github.io/momapy/
- **Issues**: https://github.com/adrienrougny/momapy/issues

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

**Note**: Tests use `BEZIER_NO_EXTENSION=1` (disables bezier C extension). Slow tests are marked `@pytest.mark.slow`.

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
│   └── io/sbgnml.py  # SBGN-ML I/O
├── celldesigner/     # CellDesigner format support
├── sbml/             # SBML support
├── rendering/        # Backends: svg_native, skia, cairo
├── io/core.py        # Reader/Writer base classes, ReaderResult, WriterResult
└── plugins/core.py   # Plugin registry with lazy loading
tests/
docs/
```

## Tech Stack

- **Python**: 3.10–3.12
- **Key deps**: numpy, shapely, bezier, lxml, frozendict, pyparsing, uharfbuzz, matplotlib
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
- Complex operations: use `shapely`

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

- **Tests** (`.github/workflows/tests.yml`): ubuntu + windows + macos, Python 3.10/3.11/3.12
- **Release** (`.github/workflows/release.yml`): triggered by `v*.*.*` tags → test → build → publish to PyPI → generate changelog → GitHub release
- **Docs** (`.github/workflows/docs.yml`): deploy to GitHub Pages after release

## DO / DON'T

**DO:**
- Use frozen dataclasses for model/layout elements
- Use builder pattern for modifications
- Add type hints and Google-style docstrings everywhere
- Mark slow tests with `@pytest.mark.slow`
- Use conventional commits

**DON'T:**
- Mutate frozen dataclasses directly
- Skip type hints or docstrings
- Bypass test coverage (70% minimum)
- Add unnecessary complexity or premature abstractions
