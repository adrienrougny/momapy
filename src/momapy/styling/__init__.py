"""Classes and functions for styling layout elements using style sheets.

This subpackage provides a CSS-like styling system for layout elements,
supporting:

- Style sheets with selectors (type, class, id, child, descendant, compound)
- Style collections that group related style properties
- CSS parsing from files or strings
- Style application to layout elements

Examples:
    ```python
    from momapy.styling import StyleSheet, apply_style_sheet

    stylesheet = StyleSheet.from_file("styles.css")
    styled_element = apply_style_sheet(element, stylesheet)
    ```
"""

from momapy.styling.core import StyleCollection as StyleCollection
from momapy.styling.core import StyleSheet as StyleSheet
from momapy.styling.core import Selector as Selector
from momapy.styling.core import TypeSelector as TypeSelector
from momapy.styling.core import ClassSelector as ClassSelector
from momapy.styling.core import IdSelector as IdSelector
from momapy.styling.core import ChildSelector as ChildSelector
from momapy.styling.core import DescendantSelector as DescendantSelector
from momapy.styling.core import OrSelector as OrSelector
from momapy.styling.core import CompoundSelector as CompoundSelector
from momapy.styling.core import NotSelector as NotSelector
from momapy.styling.core import combine_style_sheets as combine_style_sheets
from momapy.styling.core import apply_style_collection as apply_style_collection
from momapy.styling.core import apply_style_sheet as apply_style_sheet
from momapy.styling.core import get_stylable_attributes as get_stylable_attributes

__all__ = [
    "StyleCollection",
    "StyleSheet",
    "Selector",
    "TypeSelector",
    "ClassSelector",
    "IdSelector",
    "ChildSelector",
    "DescendantSelector",
    "OrSelector",
    "CompoundSelector",
    "NotSelector",
    "combine_style_sheets",
    "apply_style_collection",
    "apply_style_sheet",
    "get_stylable_attributes",
]
