"""Tests for the reading and writing of CellDesigner modification states."""

import os

import lxml.etree
import pytest

import momapy.io.core
from momapy.celldesigner.model import ModificationState

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(TEST_DIR, "..", "fixtures", "modification_states.xml")

_CD_NS = "http://www.sbml.org/2001/ns/celldesigner"

RESIDUE_TO_CD_STATE = {
    "rs1": "phosphorylated",
    "rs2": "acetylated",
    "rs3": "ubiquitinated",
    "rs4": "methylated",
    "rs5": "hydroxylated",
    "rs6": "glycosylated",
    "rs7": "myristoylated",
    "rs8": "palmytoylated",
    "rs9": "prenylated",
    "rs10": "protonated",
    "rs11": "sulfated",
    "rs12": "don't care",
    "rs13": "unknown",
    "rs14": "empty",
}


def test_read():
    map_ = momapy.io.core.read(FIXTURE).obj
    species = next(iter(map_.model.species))
    residue_name_to_state = {
        modification.residue.name: modification.state
        for modification in species.modifications
    }
    assert residue_name_to_state["r8"] is ModificationState.PALMITOYLATED
    assert residue_name_to_state["r12"] is ModificationState.DON_T_CARE
    assert residue_name_to_state["r14"] is None
    assert len(residue_name_to_state) == len(RESIDUE_TO_CD_STATE)


@pytest.mark.parametrize("residue_id", list(RESIDUE_TO_CD_STATE))
def test_round_trip(tmp_path, residue_id):
    result = momapy.io.core.read(FIXTURE)
    output_file = tmp_path / "output.xml"
    momapy.io.core.write(
        result.obj,
        str(output_file),
        writer="celldesigner",
        source_id_to_model_element=result.source_id_to_model_element,
        source_id_to_layout_element=result.source_id_to_layout_element,
    )
    root = lxml.etree.parse(str(output_file)).getroot()
    modifications = root.findall(".//cd:modification", {"cd": _CD_NS})
    residue_id_to_state = {
        modification.get("residue"): modification.get("state")
        for modification in modifications
    }
    assert residue_id_to_state[residue_id] == RESIDUE_TO_CD_STATE[residue_id]
