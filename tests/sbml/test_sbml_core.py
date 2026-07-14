"""Tests for momapy.sbml module."""


class TestSBMLModule:
    """Tests for SBML module imports and basic functionality."""

    def test_sbml_import(self):
        """Test that sbml package can be imported."""
        import momapy.sbml

        assert momapy.sbml is not None

    def test_sbml_model_import(self):
        """Test that sbml.model module can be imported."""
        import momapy.sbml.model

        assert momapy.sbml.model is not None

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
        import momapy.sbml

        model = momapy.sbml.SBMLModel()
        assert model is not None

    def test_model_has_expected_attributes(self):
        """Test that SBML model has expected attributes."""
        import momapy.sbml

        model = momapy.sbml.SBMLModel()

        assert hasattr(model, "id_")
        assert hasattr(model, "name")


class TestSBMLGetInfo:
    """Tests for momapy.sbml.utils.get_info."""

    def test_get_info_with_model(self):
        """get_info summarizes a populated model."""
        import momapy.sbml
        import momapy.sbml.utils

        map_ = momapy.sbml.SBMLMap(model=momapy.sbml.SBMLModel())
        info = momapy.sbml.utils.get_info(map_)
        assert info["map_type"] == "SBML"
        assert info["model"] == {
            "compartments": 0,
            "species": 0,
            "reactions": 0,
        }
        assert info["layout"] is None

    def test_get_info_on_model_less_map_returns_none(self):
        """get_info returns model=None for a map without a model."""
        import momapy.sbml
        import momapy.sbml.utils

        map_ = momapy.sbml.SBMLMap(model=None)
        info = momapy.sbml.utils.get_info(map_)
        assert info["map_type"] == "SBML"
        assert info["model"] is None
        assert info["layout"] is None
