"""Tests for momapy.sbml.core module."""
import pytest


def test_sbml_core_import():
    """Test that sbml.core module can be imported."""
    import momapy.sbml.core
    assert momapy.sbml.core is not None


def test_sbml_io_import():
    """Test that sbml.io module can be imported."""
    try:
        import momapy.sbml.io
        assert momapy.sbml.io is not None
    except ImportError:
        # Module might not have __init__.py
        import momapy.sbml.io.sbml
        assert momapy.sbml.io.sbml is not None
