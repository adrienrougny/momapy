"""Tests for momapy.sbgn.core module."""

import pytest


class TestSBGNCoreModule:
    """Tests for SBGN core module imports and basic functionality."""

    def test_sbgn_core_import(self):
        """Test that sbgn.core module can be imported."""
        import momapy.sbgn.core

        assert momapy.sbgn.core is not None

    def test_sbgn_pd_import(self):
        """Test that sbgn.pd module can be imported."""
        import momapy.sbgn.pd

        assert momapy.sbgn.pd is not None

    def test_sbgn_af_import(self):
        """Test that sbgn.af module can be imported."""
        import momapy.sbgn.af

        assert momapy.sbgn.af is not None

    def test_sbgn_utils_import(self):
        """Test that sbgn.utils module can be imported."""
        import momapy.sbgn.utils

        assert momapy.sbgn.utils is not None


class TestSBGNModelElements:
    """Tests for SBGN model element classes."""

    def test_process_creation(self):
        """Test creating a Process model element."""
        import momapy.sbgn.pd

        process = momapy.sbgn.pd.Process()
        assert process is not None

    def test_generic_process_creation(self):
        """Test creating a GenericProcess model element."""
        import momapy.sbgn.pd

        process = momapy.sbgn.pd.GenericProcess()
        assert process is not None
        assert hasattr(process, "reactants")
        assert hasattr(process, "products")
        assert hasattr(process, "reversible")

    def test_macromolecule_creation(self):
        """Test creating a Macromolecule model element."""
        import momapy.sbgn.pd

        entity = momapy.sbgn.pd.Macromolecule()
        assert entity is not None


class TestSBGNMap:
    """Tests for SBGN Map class."""

    def test_pd_map_creation(self):
        """Test creating a Process Description Map."""
        import momapy.sbgn.pd

        map_ = momapy.sbgn.pd.SBGNPDMap()
        assert map_ is not None

    def test_af_map_creation(self):
        """Test creating an Activity Flow Map."""
        import momapy.sbgn.af

        map_ = momapy.sbgn.af.SBGNAFMap()
        assert map_ is not None


class TestSBGNUtils:
    """Tests for SBGN utility functions."""

    def test_utils_module_exists(self):
        """Test that SBGN utils module exists and has expected functions."""
        import momapy.sbgn.utils

        # Check that the module exists
        assert momapy.sbgn.utils is not None
