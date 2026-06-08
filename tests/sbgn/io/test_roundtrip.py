"""Round-trip tests for SBGN import/export."""

import pytest
import tempfile
import os
import momapy.io.core

pytestmark = pytest.mark.slow


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


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestSBGNRoundTrip:
    """Tests for SBGN round-trip import/export."""

    @pytest.mark.parametrize("filename", SBGN_FILES)
    def test_roundtrip_sbgn_file(self, filename, temp_dir):
        """Test round-trip: import -> export -> import and check equality."""
        input_file = os.path.join(SBGN_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"SBGN file {filename} not found")
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj
        output_file = os.path.join(temp_dir, f"output_{filename}")
        momapy.io.core.write(map1, output_file, writer="sbgnml-0.3")
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj
        assert map1 == map2


# One biological activity per AF unit-of-information entity type. Each unit of
# information is encoded the spec-correct way: class="unit of information" with
# an <entity name="..."/> child naming the entity type.
_AF_UOI_ENTITY_NAMES = [
    "unspecified entity",
    "macromolecule",
    "simple chemical",
    "nucleic acid feature",
    "complex",
    "perturbation",
]

_AF_UOI_EXPECTED_MODEL_CLASSES = {
    "unspecified entity": "UnspecifiedEntityUnitOfInformation",
    "macromolecule": "MacromoleculeUnitOfInformation",
    "simple chemical": "SimpleChemicalUnitOfInformation",
    "nucleic acid feature": "NucleicAcidFeatureUnitOfInformation",
    "complex": "ComplexUnitOfInformation",
    "perturbation": "PerturbationUnitOfInformation",
}


def _make_af_uoi_sbgnml():
    """Build a minimal AF map with one biological activity per UoI type."""
    glyphs = []
    for i, name in enumerate(_AF_UOI_ENTITY_NAMES):
        glyphs.append(
            f'  <glyph id="a{i}" class="biological activity">\n'
            f'    <label text="A{i}"/>\n'
            f'    <bbox x="{100 + i * 200}" y="100" w="120" h="60"/>\n'
            f'    <glyph id="u{i}" class="unit of information">\n'
            f'      <entity name="{name}"/>\n'
            f'      <bbox x="{110 + i * 200}" y="94" w="24" h="12"/>\n'
            f"    </glyph>\n"
            f"  </glyph>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sbgn xmlns="http://sbgn.org/libsbgn/0.3">\n'
        '  <map language="activity flow">\n'
        + "\n".join(glyphs)
        + "\n  </map>\n</sbgn>\n"
    )


class TestSBGNAFUnitOfInformationRoundTrip:
    """Regression tests for AF unit-of-information serialization.

    AF units of information were silently lost on write because the writer
    emitted a bare entity class (e.g. ``class="macromolecule"``) instead of
    ``class="unit of information"`` with an ``<entity name="..."/>`` child,
    which the reader could not classify.
    """

    def test_af_unit_of_information_roundtrip(self, temp_dir):
        input_file = os.path.join(temp_dir, "af_uoi.sbgn")
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(_make_af_uoi_sbgnml())

        map1 = momapy.io.core.read(input_file, reader="sbgnml").obj
        read_model = {
            activity.label: [
                type(uoi).__name__ for uoi in activity.units_of_information
            ]
            for activity in map1.model.activities
        }
        expected = {
            f"A{i}": [_AF_UOI_EXPECTED_MODEL_CLASSES[name]]
            for i, name in enumerate(_AF_UOI_ENTITY_NAMES)
        }
        assert read_model == expected

        output_file = os.path.join(temp_dir, "af_uoi_out.sbgn")
        momapy.io.core.write(map1, output_file, writer="sbgnml-0.3")
        map2 = momapy.io.core.read(output_file, reader="sbgnml").obj

        # Model: every unit of information survives the round-trip unchanged.
        roundtrip_model = {
            activity.label: [
                type(uoi).__name__ for uoi in activity.units_of_information
            ]
            for activity in map2.model.activities
        }
        assert roundtrip_model == expected

        # Layout: every biological activity keeps its UoI sub-layout.
        roundtrip_layout = {
            le.label.text: [type(child).__name__ for child in le.layout_elements]
            for le in map2.layout.layout_elements
            if type(le).__name__ == "BiologicalActivityLayout"
        }
        expected_layout = {
            f"A{i}": [f"{_AF_UOI_EXPECTED_MODEL_CLASSES[name]}Layout"]
            for i, name in enumerate(_AF_UOI_ENTITY_NAMES)
        }
        assert roundtrip_layout == expected_layout

        # Full structural equality is the strongest guarantee.
        assert map1 == map2
