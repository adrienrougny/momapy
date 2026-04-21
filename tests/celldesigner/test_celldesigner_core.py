"""Tests for momapy.celldesigner core modules."""

import pytest
from momapy.celldesigner.model import CellDesignerModel


class TestCellDesignerCoreModule:
    """Tests for CellDesigner core module imports and basic functionality."""

    def test_celldesigner_core_import(self):
        """Test that celldesigner core modules can be imported."""
        import momapy.celldesigner.elements
        import momapy.celldesigner.layout
        import momapy.celldesigner.map
        import momapy.celldesigner.model

        assert momapy.celldesigner.elements is not None
        assert momapy.celldesigner.layout is not None
        assert momapy.celldesigner.map is not None
        assert momapy.celldesigner.model is not None

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
        import momapy.celldesigner.model

        # CellDesigner models are complex; just test we can import and instantiate
        model = CellDesignerModel()
        assert model is not None

    def test_model_has_expected_attributes(self):
        """Test that CellDesigner model has expected attributes."""
        import momapy.celldesigner.model

        model = CellDesignerModel()

        # Check for common model attributes
        assert hasattr(model, "id_")
        assert hasattr(model, "name")
