"""Tests for momapy.celldesigner.core module."""


def test_celldesigner_core_import():
    """Test that celldesigner.core module can be imported."""
    import momapy.celldesigner.core
    assert momapy.celldesigner.core is not None


def test_celldesigner_io_import():
    """Test that celldesigner.io module can be imported."""
    try:
        import momapy.celldesigner.io
        assert momapy.celldesigner.io is not None
    except ImportError:
        # Module might not have __init__.py
        import momapy.celldesigner.io.celldesigner
        assert momapy.celldesigner.io.celldesigner is not None
