"""Tests for SBGN reading functionality."""

import pytest
import os
import momapy.io.core
import momapy.sbgn
import momapy.sbgn.pd
import momapy.sbml.model
import momapy.core.layout
import frozendict


# Get the directory containing this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SBGN_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps", "pd")


# Discover all .sbgn files in the maps directory
def get_sbgn_files():
    """Get all SBGN files from the maps directory."""
    if not os.path.exists(SBGN_MAPS_DIR):
        return []
    return [f for f in os.listdir(SBGN_MAPS_DIR) if f.endswith(".sbgn")]


SBGN_FILES = get_sbgn_files()


class TestSBGNReading:
    """Tests for reading SBGN files."""

    @pytest.mark.parametrize("filename", SBGN_FILES)
    @pytest.mark.parametrize("return_type", ["map", "model", "layout"])
    def test_read_sbgn_file(self, filename, return_type):
        """Test reading SBGN files with all return types."""
        input_file = os.path.join(SBGN_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"SBGN file {filename} not found")
        result = momapy.io.core.read(input_file, return_type=return_type)
        assert result is not None
        assert result.obj is not None


class TestSBGNReadOptionalParameters:
    """Tests for SBGN read function optional parameters."""

    @pytest.fixture
    def test_file(self):
        """Return path to a test SBGN file."""
        if not SBGN_FILES:
            pytest.skip("No SBGN test files found")
        return os.path.join(SBGN_MAPS_DIR, SBGN_FILES[0])

    @pytest.mark.parametrize(
        "return_type,expected_type",
        [
            ("map", momapy.sbgn.SBGNMap),
            ("model", momapy.sbgn.SBGNModel),
            ("layout", momapy.core.layout.Layout),
        ],
    )
    def test_return_type_parameter(self, test_file, return_type, expected_type):
        """Test return_type parameter returns correct object type."""
        result = momapy.io.core.read(test_file, return_type=return_type)
        assert isinstance(result.obj, expected_type)

    def test_with_model_true(self, test_file):
        """Test with_model=True includes model in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.SBGNMap)
        # Verify the map has a model
        assert hasattr(result.obj, "model")
        assert result.obj.model is not None

    def test_with_model_false(self, test_file):
        """Test with_model=False excludes model from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.SBGNMap)
        # Verify the map has no model (or model is None)
        assert hasattr(result.obj, "model")
        assert result.obj.model is None

    def test_with_layout_true(self, test_file):
        """Test with_layout=True includes layout in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.SBGNMap)
        # Verify the map has a layout
        assert hasattr(result.obj, "layout")
        assert result.obj.layout is not None

    def test_with_layout_false(self, test_file):
        """Test with_layout=False excludes layout from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.SBGNMap)
        # Verify the map has no layout (or layout is None)
        assert hasattr(result.obj, "layout")
        assert result.obj.layout is None

    def test_with_annotations_true(self, test_file):
        """Test with_annotations=True includes annotations in result."""
        result = momapy.io.core.read(test_file, with_annotations=True)
        assert hasattr(result, "element_to_annotations")
        assert isinstance(result.element_to_annotations, frozendict.frozendict)
        # Annotations may be empty if file has none, but should be a frozendict

    def test_with_annotations_false(self, test_file):
        """Test with_annotations=False excludes annotations from result."""
        result = momapy.io.core.read(test_file, with_annotations=False)
        assert hasattr(result, "element_to_annotations")
        # Should be empty frozendict when with_annotations=False
        assert result.element_to_annotations == frozendict.frozendict()

    def test_with_notes_true(self, test_file):
        """Test with_notes=True includes notes in result."""
        result = momapy.io.core.read(test_file, with_notes=True)
        assert hasattr(result, "element_to_notes")
        assert isinstance(result.element_to_notes, frozendict.frozendict)
        # Notes may be empty if file has none, but should be a frozendict

    def test_with_notes_false(self, test_file):
        """Test with_notes=False excludes notes from result."""
        result = momapy.io.core.read(test_file, with_notes=False)
        assert hasattr(result, "element_to_notes")
        # Should be empty frozendict when with_notes=False
        assert result.element_to_notes == frozendict.frozendict()


ANNOTATED_FILE = os.path.join(SBGN_MAPS_DIR, "simple_annotated.sbgn")


class TestSBGNAnnotationsContent:
    """Tests that annotations are correctly parsed from SBGN-ML files.

    Uses simple_annotated.sbgn which has RDF annotations on two
    macromolecule glyphs (ERK and MEK).
    """

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(ANNOTATED_FILE):
            pytest.skip("simple_annotated.sbgn not found")
        return momapy.io.core.read(
            ANNOTATED_FILE, with_annotations=True, with_notes=True
        )

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
                assert isinstance(a, momapy.sbml.model.RDFAnnotation)

    def test_erk_annotations(self, result):
        """Test annotations on glyph1 (ERK macromolecule)."""
        annots = self._get_annotations_by_id(result, "glyph1_model")
        assert len(annots) == 2
        qualifiers = {a.qualifier for a in annots}
        assert qualifiers == {
            momapy.sbml.model.BQBiol.IS,
            momapy.sbml.model.BQBiol.IS_DESCRIBED_BY,
        }
        resources = {r for a in annots for r in a.resources}
        assert "urn:miriam:uniprot:P28482" in resources
        assert "urn:miriam:pubmed:12345678" in resources

    def test_mek_annotation(self, result):
        """Test annotation on glyph2 (MEK macromolecule)."""
        annots = self._get_annotations_by_id(result, "glyph2_model")
        assert len(annots) == 1
        annotation = next(iter(annots))
        assert annotation.qualifier == momapy.sbml.model.BQBiol.IS
        assert annotation.resources == frozenset({"urn:miriam:uniprot:Q02750"})

    def test_annotated_elements_are_macromolecules(self, result):
        """Test that annotated elements are Macromolecule instances."""
        for elem, annots in result.element_to_annotations.items():
            if annots:
                assert isinstance(elem, momapy.sbgn.pd.Macromolecule)

    def test_with_annotations_false_produces_empty(self):
        """Test that with_annotations=False produces no annotations."""
        if not os.path.exists(ANNOTATED_FILE):
            pytest.skip("simple_annotated.sbgn not found")
        result = momapy.io.core.read(ANNOTATED_FILE, with_annotations=False)
        assert result.element_to_annotations == frozendict.frozendict()


class TestSBGNNotesContent:
    """Tests that notes are correctly parsed from SBGN-ML files.

    Uses simple_annotated.sbgn which has notes on the ERK glyph.
    """

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(ANNOTATED_FILE):
            pytest.skip("simple_annotated.sbgn not found")
        return momapy.io.core.read(
            ANNOTATED_FILE, with_annotations=True, with_notes=True
        )

    def test_notes_are_non_empty(self, result):
        """Test that the file produces a non-empty notes dict."""
        non_empty = {
            elem: notes for elem, notes in result.element_to_notes.items() if notes
        }
        assert len(non_empty) > 0

    def test_notes_values_are_frozensets_of_strings(self, result):
        """Test that each value is a frozenset of str."""
        for elem, notes in result.element_to_notes.items():
            assert isinstance(notes, frozenset)
            for n in notes:
                assert isinstance(n, str)

    def test_erk_notes_content(self, result):
        """Test that glyph1 (ERK) has notes with expected content."""
        for elem, notes in result.element_to_notes.items():
            if getattr(elem, "id_", None) == "glyph1_model" and notes:
                assert len(notes) == 1
                note = next(iter(notes))
                assert "ERK is a MAP kinase" in note
                assert "<html" in note
                return
        pytest.fail("No notes found for glyph1 (ERK)")

    def test_mek_has_no_notes(self, result):
        """Test that glyph2 (MEK) has no notes."""
        for elem, notes in result.element_to_notes.items():
            if getattr(elem, "id_", None) == "glyph2_model":
                assert len(notes) == 0
                return

    def test_with_notes_false_produces_empty(self):
        """Test that with_notes=False produces no notes."""
        if not os.path.exists(ANNOTATED_FILE):
            pytest.skip("simple_annotated.sbgn not found")
        result = momapy.io.core.read(ANNOTATED_FILE, with_notes=False)
        assert result.element_to_notes == frozendict.frozendict()
