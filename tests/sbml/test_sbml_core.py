"""Tests for momapy.sbml.core module."""

import pytest


class TestSBMLCoreModule:
    """Tests for SBML core module imports and basic functionality."""

    def test_sbml_core_import(self):
        """Test that sbml.core module can be imported."""
        import momapy.sbml.core

        assert momapy.sbml.core is not None

    def test_sbml_io_import(self):
        """Test that sbml.io module can be imported."""
        try:
            import momapy.sbml.io

            assert momapy.sbml.io is not None
        except ImportError:
            # Module might not have __init__.py
            import momapy.sbml.io.sbml

            assert momapy.sbml.io.sbml is not None


class TestSBMLModel:
    """Tests for SBML model classes."""

    def test_model_creation(self):
        """Test creating an SBML model."""
        import momapy.sbml.core

        model = momapy.sbml.core.Model()
        assert model is not None

    def test_model_has_expected_attributes(self):
        """Test that SBML model has expected attributes."""
        import momapy.sbml.core

        model = momapy.sbml.core.Model()

        # Check for common model attributes
        assert hasattr(model, "id_")
        assert hasattr(model, "name")
