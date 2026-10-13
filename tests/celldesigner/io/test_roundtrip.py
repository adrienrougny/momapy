"""Round-trip tests for CellDesigner import/export."""

import lxml.etree
import pytest
import tempfile
import os
import momapy.io.core

pytestmark = pytest.mark.slow


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CD_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps")


def get_cd_files():
    """Get all CellDesigner XML files from the maps directory."""
    if not os.path.exists(CD_MAPS_DIR):
        return []
    return [f for f in os.listdir(CD_MAPS_DIR) if f.endswith(".xml")]


CD_FILES = get_cd_files()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestCellDesignerRoundTrip:
    """Tests for CellDesigner round-trip import/export."""

    @pytest.mark.parametrize("filename", CD_FILES)
    def test_roundtrip_cd_file(self, filename, temp_dir):
        """Test round-trip: import -> export -> import and check model equality."""
        input_file = os.path.join(CD_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"CellDesigner file {filename} not found")
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj
        output_file = os.path.join(temp_dir, f"output_{filename}")
        momapy.io.core.write(map1, output_file, writer="celldesigner")
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj
        assert map1.model == map2.model


COMPARTMENT_ALIAS_FILES = [
    os.path.join(TEST_DIR, "..", "fixtures", "inhibition_phenotype.xml"),
    os.path.join(TEST_DIR, "..", "fixtures", "self_modulation.xml"),
    os.path.join(CD_MAPS_DIR, "Apoptosis_pathway.xml"),
    os.path.join(CD_MAPS_DIR, "FOXO3_activity.xml"),
]


def get_top_level_compartment_aliases(root):
    sbml_namespace = root.nsmap[None]
    celldesigner_namespace = "http://www.sbml.org/2001/ns/celldesigner"
    species_id_to_compartment_id = {
        species.get("id"): species.get("compartment")
        for species in root.iter(f"{{{sbml_namespace}}}species")
    }
    compartment_alias_id_to_compartment_id = {
        compartment_alias.get("id"): compartment_alias.get("compartment")
        for compartment_alias in root.iter(
            f"{{{celldesigner_namespace}}}compartmentAlias"
        )
    }
    alias_id_to_compartment_alias_id = {}
    for tag in ("speciesAlias", "complexSpeciesAlias"):
        for alias in root.iter(f"{{{celldesigner_namespace}}}{tag}"):
            compartment_alias_id = alias.get("compartmentAlias")
            if compartment_alias_id is None:
                continue
            alias_id_to_compartment_alias_id[alias.get("id")] = (
                compartment_alias_id,
                compartment_alias_id_to_compartment_id.get(compartment_alias_id)
                == species_id_to_compartment_id.get(alias.get("species")),
            )
    return alias_id_to_compartment_alias_id


@pytest.mark.parametrize("input_file", COMPARTMENT_ALIAS_FILES)
def test_roundtrip_keeps_compartment_alias(input_file, temp_dir):
    map_ = momapy.io.core.read(input_file).obj
    output_file = os.path.join(temp_dir, "output.xml")
    momapy.io.core.write(map_, output_file, writer="celldesigner")
    input_aliases = get_top_level_compartment_aliases(
        lxml.etree.parse(input_file).getroot()
    )
    output_aliases = get_top_level_compartment_aliases(
        lxml.etree.parse(output_file).getroot()
    )
    for alias_id, (compartment_alias_id, is_consistent) in input_aliases.items():
        if is_consistent:
            assert output_aliases[alias_id][0] == compartment_alias_id
