"""Tests for momapy.celldesigner.core module."""

import pytest


class TestCellDesignerCoreModule:
    """Tests for CellDesigner core module imports and basic functionality."""

    def test_celldesigner_core_import(self):
        """Test that celldesigner.core module can be imported."""
        import momapy.celldesigner.core

        assert momapy.celldesigner.core is not None

    def test_celldesigner_io_import(self):
        """Test that celldesigner.io module can be imported."""
        try:
            import momapy.celldesigner.io

            assert momapy.celldesigner.io is not None
        except ImportError:
            # Module might not have __init__.py
            import momapy.celldesigner.io.celldesigner

            assert momapy.celldesigner.io.celldesigner is not None


class TestCellDesignerModel:
    """Tests for CellDesigner model classes."""

    def test_model_creation(self):
        """Test creating a CellDesigner model."""
        import momapy.celldesigner.core

        # CellDesigner models are complex; just test we can import and instantiate
        model = momapy.celldesigner.core.CellDesignerModel()
        assert model is not None

    def test_model_has_expected_attributes(self):
        """Test that CellDesigner model has expected attributes."""
        import momapy.celldesigner.core

        model = momapy.celldesigner.core.CellDesignerModel()

        # Check for common model attributes
        assert hasattr(model, "id_")
        assert hasattr(model, "name")
