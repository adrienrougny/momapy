"""Tests for SBML reading functionality."""

import pytest
import os
import momapy.sbml.core
import momapy.sbml.io.sbml.reader
import frozendict


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SBML_MODELS_DIR = os.path.join(TEST_DIR, "models")


def get_sbml_files():
    """Get all SBML XML files from the models directory."""
    if not os.path.exists(SBML_MODELS_DIR):
        return []
    return sorted(f for f in os.listdir(SBML_MODELS_DIR) if f.endswith(".xml"))


SBML_FILES = get_sbml_files()


class TestSBMLReading:
    """Tests for reading SBML files."""

    @pytest.mark.parametrize("filename", SBML_FILES)
    def test_read_sbml_file(self, filename):
        """Test that each SBML file can be read without error."""
        path = os.path.join(SBML_MODELS_DIR, filename)
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(path)
        assert result is not None
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbml.core.SBMLModel)

    @pytest.mark.parametrize("filename", SBML_FILES)
    def test_read_produces_model_with_content(self, filename):
        """Test that each SBML file produces a model with compartments/species/reactions."""
        path = os.path.join(SBML_MODELS_DIR, filename)
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(path)
        model = result.obj
        assert len(model.compartments) > 0 or len(model.species) > 0


class TestSBMLReadOptionalParameters:
    """Tests for SBML read function optional parameters."""

    @pytest.fixture
    def test_file(self):
        """Return path to a test SBML file."""
        if not SBML_FILES:
            pytest.skip("No SBML test files found")
        return os.path.join(SBML_MODELS_DIR, SBML_FILES[0])

    def test_with_annotations_true(self, test_file):
        """Test with_annotations=True includes annotations in result."""
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(
            test_file, with_annotations=True
        )
        assert isinstance(result.annotations, frozendict.frozendict)

    def test_with_annotations_false(self, test_file):
        """Test with_annotations=False excludes annotations from result."""
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(
            test_file, with_annotations=False
        )
        assert result.annotations == frozendict.frozendict()

    def test_with_notes_true(self, test_file):
        """Test with_notes=True includes notes in result."""
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(
            test_file, with_notes=True
        )
        assert isinstance(result.notes, frozendict.frozendict)

    def test_with_notes_false(self, test_file):
        """Test with_notes=False excludes notes from result."""
        result = momapy.sbml.io.sbml.reader.SBMLReader.read(
            test_file, with_notes=False
        )
        assert result.notes == frozendict.frozendict()


class TestSBMLAnnotationsContent:
    """Tests that annotations are correctly parsed from SBML files.

    Uses glimepiride_body_flat.xml which has annotations on compartments,
    species, reactions, and the model itself.
    """

    GLIMEPIRIDE = os.path.join(SBML_MODELS_DIR, "glimepiride_body_flat.xml")

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(self.GLIMEPIRIDE):
            pytest.skip("glimepiride_body_flat.xml not found")
        return momapy.sbml.io.sbml.reader.SBMLReader.read(
            self.GLIMEPIRIDE, with_annotations=True, with_notes=True
        )

    def _get_element_by_id(self, result, id_):
        """Find an annotated element by its id_."""
        for elem in result.annotations:
            if getattr(elem, "id_", None) == id_:
                return elem
        return None

    def _get_annotations_by_id(self, result, id_):
        """Get the frozenset of annotations for an element by its id_."""
        elem = self._get_element_by_id(result, id_)
        if elem is not None:
            return result.annotations.get(elem, frozenset())
        return frozenset()

    def test_annotations_are_non_empty(self, result):
        """Test that the file produces a non-empty annotations dict."""
        non_empty = {
            elem: annots
            for elem, annots in result.annotations.items()
            if annots
        }
        assert len(non_empty) > 0

    def test_annotation_values_are_frozensets_of_rdf_annotations(self, result):
        """Test that each value is a frozenset of RDFAnnotation objects."""
        for elem, annots in result.annotations.items():
            assert isinstance(annots, frozenset)
            for a in annots:
                assert isinstance(a, momapy.sbml.core.RDFAnnotation)

    def test_compartment_annotation(self, result):
        """Test annotations on compartment Vre."""
        annots = self._get_annotations_by_id(result, "Vre")
        assert len(annots) == 3
        qualifiers = {a.qualifier for a in annots}
        assert momapy.sbml.core.BQBiol.IS in qualifiers
        assert momapy.sbml.core.BQBiol.IS_PART_OF in qualifiers

    def test_species_annotation(self, result):
        """Test annotations on species Cki_plasma_gli."""
        annots = self._get_annotations_by_id(result, "Cki_plasma_gli")
        assert len(annots) >= 1
        resources = {r for a in annots for r in a.resources}
        assert "http://identifiers.org/CHEBI:5383" in resources

    def test_model_level_annotations(self, result):
        """Test that the model object itself has annotations."""
        model_annots = result.annotations.get(result.obj)
        assert model_annots is not None
        assert len(model_annots) > 0

    def test_annotations_span_multiple_element_types(self, result):
        """Test that annotations cover compartments, species, reactions, and the model."""
        types_with_annotations = {
            type(elem).__name__
            for elem, annots in result.annotations.items()
            if annots
        }
        assert "Compartment" in types_with_annotations
        assert "Species" in types_with_annotations
        assert "Reaction" in types_with_annotations
        assert "SBMLModel" in types_with_annotations


class TestSBMLNotesContent:
    """Tests that notes are correctly parsed from SBML files.

    Uses glimepiride_body_flat.xml which has notes on reactions and the model.
    """

    GLIMEPIRIDE = os.path.join(SBML_MODELS_DIR, "glimepiride_body_flat.xml")

    @pytest.fixture(scope="class")
    def result(self):
        if not os.path.exists(self.GLIMEPIRIDE):
            pytest.skip("glimepiride_body_flat.xml not found")
        return momapy.sbml.io.sbml.reader.SBMLReader.read(
            self.GLIMEPIRIDE, with_annotations=True, with_notes=True
        )

    def test_notes_are_non_empty(self, result):
        """Test that the file produces a non-empty notes dict."""
        non_empty = {
            elem: notes
            for elem, notes in result.notes.items()
            if notes
        }
        assert len(non_empty) > 0

    def test_notes_values_are_frozensets_of_strings(self, result):
        """Test that each value is a frozenset of str."""
        for elem, notes in result.notes.items():
            assert isinstance(notes, frozenset)
            for n in notes:
                assert isinstance(n, str)

    def test_notes_contain_xml(self, result):
        """Test that note strings are valid XML fragments."""
        for elem, notes in result.notes.items():
            for n in notes:
                assert n.startswith("<")
                return

    def test_model_level_notes(self, result):
        """Test that the model object has notes."""
        model_notes = result.notes.get(result.obj)
        assert model_notes is not None
        assert len(model_notes) == 1
        note = next(iter(model_notes))
        assert isinstance(note, str)
        assert "<body" in note or "<p" in note

    def test_reaction_notes(self, result):
        """Test that at least one reaction has notes."""
        reaction_notes = {
            elem: notes
            for elem, notes in result.notes.items()
            if type(elem).__name__ == "Reaction" and notes
        }
        assert len(reaction_notes) > 0

    def test_notes_span_multiple_element_types(self, result):
        """Test that notes cover reactions and the model."""
        types_with_notes = {
            type(elem).__name__
            for elem, notes in result.notes.items()
            if notes
        }
        assert "Reaction" in types_with_notes
        assert "SBMLModel" in types_with_notes
