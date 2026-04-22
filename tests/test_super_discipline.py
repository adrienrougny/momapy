"""Discipline test: forbid raw `super(...)` in the frozen hierarchy.

Builder classes form a parallel class hierarchy that does not inherit
from the frozen original classes.  Because of that, `super()` (zero-arg)
and `super(OriginalClass, self)` (three-arg) raise
`TypeError: obj must be an instance or subtype of type` whenever `self`
is a builder instance — which happens every time a layout-tidying or
fitting utility queries geometry on a builder layout.

The safe replacement is
`momapy.builder.super_or_builder(OriginalClass, self).method(...)`,
which falls back to the builder super proxy when the original fails.

This test scans modules that host frozen dataclasses with builder
counterparts and fails if any raw `super(...)` call appears.  Purely
lexical mentions in docstrings/comments are ignored because the check
runs against the parsed AST, not the source text.
"""

import ast
import pathlib


FROZEN_HIERARCHY_PATHS = [
    "src/momapy/core/elements.py",
    "src/momapy/core/model.py",
    "src/momapy/core/layout.py",
    "src/momapy/core/map.py",
    "src/momapy/sbgn",
    "src/momapy/celldesigner",
    "src/momapy/sbml",
    "src/momapy/meta",
]


def _python_files():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    for entry in FROZEN_HIERARCHY_PATHS:
        path = repo_root / entry
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from sorted(path.rglob("*.py"))


def test_no_raw_super_in_frozen_hierarchy():
    offenders = []
    for path in _python_files():
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "super"
            ):
                offenders.append(f"{path}:{node.lineno}")
    assert not offenders, (
        "Raw `super(...)` calls found in the frozen hierarchy. Use "
        "`momapy.builder.super_or_builder(OriginalClass, self)` instead "
        "so builder instances do not raise TypeError.\n" + "\n".join(offenders)
    )
