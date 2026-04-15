"""Tests for CellDesigner reading functionality."""

import pytest
import os
import momapy.io.core
import momapy.celldesigner.core
import momapy.core.layout
import momapy.sbml.core
import frozendict


# Get the directory containing this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CELLDESIGNER_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps")

# Discover all .xml files in the maps directory
def get_celldesigner_files():
    """Get all CellDesigner XML files from the maps directory."""
    if not os.path.exists(CELLDESIGNER_MAPS_DIR):
        return []
    return [f for f in os.listdir(CELLDESIGNER_MAPS_DIR) if f.endswith('.xml')]

CELLDESIGNER_FILES = get_celldesigner_files()


class TestCellDesignerReading:
    """Tests for reading CellDesigner files."""

    @pytest.mark.parametrize("filename", CELLDESIGNER_FILES)
    def test_read_celldesigner_file(self, filename):
        """Test reading CellDesigner XML files."""
        input_file = os.path.join(CELLDESIGNER_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"CellDesigner file {filename} not found")
        result = momapy.io.core.read(input_file)
        assert result is not None
        assert result.obj is not None
        # Verify we got a map object
        assert hasattr(result.obj, 'layout')


class TestCellDesignerReadOptionalParameters:
    """Tests for CellDesigner read function optional parameters."""

    @pytest.fixture
    def test_file(self):
        """Return path to a test CellDesigner file."""
        if not CELLDESIGNER_FILES:
            pytest.skip("No CellDesigner test files found")
        return os.path.join(CELLDESIGNER_MAPS_DIR, CELLDESIGNER_FILES[0])

    @pytest.mark.parametrize("return_type,expected_type", [
        ("map", momapy.celldesigner.core.CellDesignerMap),
        ("model", momapy.celldesigner.core.CellDesignerModel),
        ("layout", momapy.core.layout.Layout),
    ])
    def test_return_type_parameter(self, test_file, return_type, expected_type):
        """Test return_type parameter returns correct object type."""
        result = momapy.io.core.read(test_file, return_type=return_type)
        assert isinstance(result.obj, expected_type)

    def test_with_model_true(self, test_file):
        """Test with_model=True includes model in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.celldesigner.core.CellDesignerMap)
        # Verify the map has a model
        assert hasattr(result.obj, 'model')
        assert result.obj.model is not None

    def test_with_model_false(self, test_file):
        """Test with_model=False excludes model from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.celldesigner.core.CellDesignerMap)
        # Verify the map has no model (or model is None)
        assert hasattr(result.obj, 'model')
        assert result.obj.model is None

    def test_with_layout_true(self, test_file):
        """Test with_layout=True includes layout in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.celldesigner.core.CellDesignerMap)
        # Verify the map has a layout
        assert hasattr(result.obj, 'layout')
        assert result.obj.layout is not None

    def test_with_layout_false(self, test_file):
        """Test with_layout=False excludes layout from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.celldesigner.core.CellDesignerMap)
        # Verify the map has no layout (or layout is None)
        assert hasattr(result.obj, 'layout')
        assert result.obj.layout is None

    def test_with_annotations_true(self, test_file):
        """Test with_annotations=True includes annotations in result."""
        result = momapy.io.core.read(test_file, with_annotations=True)
        assert hasattr(result, 'element_to_annotations')
        assert isinstance(result.element_to_annotations, frozendict.frozendict)
        # Annotations may be empty if file has none, but should be a frozendict

    def test_with_annotations_false(self, test_file):
        """Test with_annotations=False excludes annotations from result."""
        result = momapy.io.core.read(test_file, with_annotations=False)
        assert hasattr(result, 'element_to_annotations')
        # Should be empty frozendict when with_annotations=False
        assert result.element_to_annotations == frozendict.frozendict()

    def test_with_notes_true(self, test_file):
        """Test with_notes=True includes notes in result."""
        result = momapy.io.core.read(test_file, with_notes=True)
        assert hasattr(result, 'element_to_notes')
        assert isinstance(result.element_to_notes, frozendict.frozendict)
        # Notes may be empty if file has none, but should be a frozendict

    def test_with_notes_false(self, test_file):
        """Test with_notes=False excludes notes from result."""
        result = momapy.io.core.read(test_file, with_notes=False)
        assert hasattr(result, 'element_to_notes')
        # Should be empty frozendict when with_notes=False
        assert result.element_to_notes == frozendict.frozendict()


class TestCellDesignerAnnotationsContent:
    """Tests that annotations are correctly parsed from CellDesigner files.

    Uses Apoptosis_pathway.xml which contains RDF annotations on compartments,
    species, and reactions.
    """

    APOPTOSIS = os.path.join(CELLDESIGNER_MAPS_DIR, "Apoptosis_pathway.xml")

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(self.APOPTOSIS):
            pytest.skip("Apoptosis_pathway.xml not found")
        return momapy.io.core.read(self.APOPTOSIS, with_annotations=True, with_notes=True)

    def _get_element_by_id(self, result, id_):
        """Find an annotated element by its id_."""
        for elem in result.element_to_annotations:
            if getattr(elem, "id_", None) == id_:
                return elem
        return None

    def _get_annotations_by_id(self, result, id_):
        """Get the frozenset of annotations for an element by its id_."""
        elem = self._get_element_by_id(result, id_)
        if elem is not None:
            return result.element_to_annotations.get(elem, frozenset())
        return frozenset()

    def test_annotations_are_non_empty(self, result):
        """Test that the file produces a non-empty annotations dict."""
        non_empty = {
            elem: annots
            for elem, annots in result.element_to_annotations.items()
            if annots
        }
        assert len(non_empty) > 0

    def test_annotation_values_are_frozensets_of_rdf_annotations(self, result):
        """Test that each value is a frozenset of RDFAnnotation objects."""
        for elem, annots in result.element_to_annotations.items():
            assert isinstance(annots, frozenset)
            for a in annots:
                assert isinstance(a, momapy.sbml.core.RDFAnnotation)

    def test_compartment_annotation(self, result):
        """Test annotation on compartment s_id_ca4 (plasma membrane)."""
        annots = self._get_annotations_by_id(result, "s_id_ca4")
        assert len(annots) == 1
        annotation = next(iter(annots))
        assert annotation.qualifier == momapy.sbml.core.BQBiol.IS
        assert annotation.resources == frozenset(
            {"urn:miriam:obo.go:GO%3A0005886"}
        )

    def test_species_annotations(self, result):
        """Test annotations on species s_id_sa30 (BAX protein)."""
        annots = self._get_annotations_by_id(result, "s_id_sa30")
        assert len(annots) == 6
        qualifiers = {a.qualifier for a in annots}
        assert qualifiers == {momapy.sbml.core.BQBiol.IS_DESCRIBED_BY}
        resources = {r for a in annots for r in a.resources}
        assert "urn:miriam:uniprot:Q07812" in resources
        assert "urn:miriam:hgnc.symbol:BAX" in resources
        assert "urn:miriam:hgnc:959" in resources

    def test_annotations_span_multiple_element_types(self, result):
        """Test that annotations cover compartments, species, and reactions."""
        types_with_annotations = {
            type(elem).__name__
            for elem, annots in result.element_to_annotations.items()
            if annots
        }
        assert "Compartment" in types_with_annotations
        assert "GenericProtein" in types_with_annotations
        assert "StateTransition" in types_with_annotations


class TestCellDesignerNotesContent:
    """Tests that notes are correctly parsed from CellDesigner files.

    Uses Apoptosis_pathway.xml which contains notes on compartments,
    species, and the map itself.
    """

    APOPTOSIS = os.path.join(CELLDESIGNER_MAPS_DIR, "Apoptosis_pathway.xml")

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(self.APOPTOSIS):
            pytest.skip("Apoptosis_pathway.xml not found")
        return momapy.io.core.read(self.APOPTOSIS, with_annotations=True, with_notes=True)

    def test_notes_are_non_empty(self, result):
        """Test that the file produces a non-empty notes dict."""
        non_empty = {
            elem: notes
            for elem, notes in result.element_to_notes.items()
            if notes
        }
        assert len(non_empty) > 0

    def test_notes_values_are_frozensets_of_strings(self, result):
        """Test that each value is a frozenset of str."""
        for elem, notes in result.element_to_notes.items():
            assert isinstance(notes, frozenset)
            for n in notes:
                assert isinstance(n, str)

    def test_notes_contain_xml(self, result):
        """Test that note strings are valid XML fragments."""
        for elem, notes in result.element_to_notes.items():
            for n in notes:
                assert n.startswith("<")
                break
            break

    def test_map_level_notes(self, result):
        """Test that the map object has notes."""
        map_notes = result.element_to_notes.get(result.obj)
        assert map_notes is not None
        assert len(map_notes) == 1
        note = next(iter(map_notes))
        assert isinstance(note, str)
        assert "<html" in note

    def test_compartment_notes_contain_description(self, result):
        """Test that compartment s_id_ca4 (plasma membrane) has notes."""
        for elem, notes in result.element_to_notes.items():
            if getattr(elem, "id_", None) == "s_id_ca4" and notes:
                note = next(iter(notes))
                assert "plasma membrane" in note
                return
        pytest.fail("No notes found for compartment s_id_ca4")

    def test_notes_span_multiple_element_types(self, result):
        """Test that notes cover compartments, species, and the map."""
        types_with_notes = {
            type(elem).__name__
            for elem, notes in result.element_to_notes.items()
            if notes
        }
        assert "Compartment" in types_with_notes
        assert "GenericProtein" in types_with_notes
        assert "CellDesignerMap" in types_with_notes


class TestCellDesignerEmptyModifications:
    """Test that modification residues absent from listOfModifications are
    stored as Modification(state=None), matching the state="empty" behaviour.

    Uses Neuroinflammation.xml which contains MAPK14 (protein p_7, residues
    T180/mr_re_1_1 and Y182/mr_re_2_1):

    - s_id_ne10f: empty <listOfModifications> → both residues should appear
      with state=None after the fix.
    - s_id_ne207: mr_re_1_1 listed as phosphorylated → mr_re_2_1 should be
      added with state=None by the fix.
    """

    NEUROINFLAMMATION = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "maps", "Neuroinflammation.xml"
    )

    @pytest.fixture(scope="class")
    def neuroinflammation_map(self):
        if not os.path.exists(self.NEUROINFLAMMATION):
            pytest.skip("Neuroinflammation.xml not found")
        return momapy.io.core.read(self.NEUROINFLAMMATION).obj

    def _get_species(self, map_, species_id):
        return next(s for s in map_.model.species if s.id_ == species_id)

    def test_empty_list_of_modifications_creates_residues_from_template(
        self, neuroinflammation_map
    ):
        # s_id_ne10f has an empty <listOfModifications>; p_7 template defines
        # two residues, so both must appear with state=None.
        species = self._get_species(neuroinflammation_map, "s_id_ne10f")
        assert len(species.modifications) == 2
        for mod in species.modifications:
            assert mod.state is None

    def test_partial_list_of_modifications_fills_uncovered_residues(
        self, neuroinflammation_map
    ):
        # s_id_ne207 has mr_re_1_1 explicitly listed as phosphorylated.
        # The fix must add mr_re_2_1 with state=None.
        species = self._get_species(neuroinflammation_map, "s_id_ne207")
        assert len(species.modifications) == 2
        states = {mod.state for mod in species.modifications}
        assert momapy.celldesigner.core.ModificationState.PHOSPHORYLATED in states
        assert None in states
