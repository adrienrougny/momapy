"""Tests for momapy.celldesigner core modules."""

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

        # CellDesigner models are complex; just test we can import and instantiate
        model = CellDesignerModel()
        assert model is not None

    def test_model_has_expected_attributes(self):
        """Test that CellDesigner model has expected attributes."""

        model = CellDesignerModel()

        # Check for common model attributes
        assert hasattr(model, "id_")
        assert hasattr(model, "name")


class TestCellDesignerRoles:
    """Tests for the shared species-reference base of CellDesigner roles."""

    def test_all_roles_share_simple_species_reference(self):
        """Reactant, Product, Modulator and gate input share the base."""
        from momapy.sbml.model import SimpleSpeciesReference
        import momapy.celldesigner.model as cd

        for cls in (
            cd.Reactant,
            cd.Product,
            cd.Modulator,
            cd.BooleanLogicGateInput,
        ):
            assert issubclass(cls, SimpleSpeciesReference)

    def test_boolean_logic_gate_input_has_referred_element(self):
        """A gate input carries referred_element from the shared base."""
        import momapy.celldesigner.model as cd

        species = cd.Protein(template=cd.ProteinTemplate(name="p"))
        gate_input = cd.BooleanLogicGateInput(referred_element=species)
        assert gate_input.referred_element is species
