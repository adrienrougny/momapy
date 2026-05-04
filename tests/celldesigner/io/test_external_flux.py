"""Tests for round-tripping external source/sink reactions through the
CellDesigner reader and writer.

The fixture `external_flux.xml` contains:

- R1: degraded -> real species (drives ``has_external_source=True``)
- R2: real species -> degraded (drives ``has_external_sink=True``)

The writer must emit DEGRADED species + aliases + base participants from
the layout alone, without mutating ``model.species``.
"""

import os

import lxml.etree
import pytest

import momapy.io.core
from momapy.celldesigner.layout import DegradedActiveLayout, DegradedLayout


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(TEST_DIR, "..", "maps", "external_flux.xml")

_CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
_SBML_NS = "http://www.sbml.org/sbml/level2/version4"


def _read(path):
    return momapy.io.core.read(path).obj


def _write(map_, path):
    return momapy.io.core.write(map_, path, writer="celldesigner")


def _reaction_by_id(map_, reaction_id):
    for r in map_.model.reactions:
        if r.id_ == reaction_id:
            return r
    raise AssertionError(f"reaction {reaction_id} not found")


def test_read_sets_external_source_flag():
    map_ = _read(FIXTURE)
    r1 = _reaction_by_id(map_, "R1")
    r2 = _reaction_by_id(map_, "R2")
    assert r1.has_external_source is True
    assert r1.has_external_sink is False
    assert r2.has_external_source is False
    assert r2.has_external_sink is True


def test_read_preserves_degraded_layouts():
    map_ = _read(FIXTURE)
    degraded = [
        le
        for le in map_.layout.layout_elements
        if isinstance(le, (DegradedLayout, DegradedActiveLayout))
    ]
    ids = sorted(le.id_ for le in degraded)
    assert ids == ["sa_deg1", "sa_deg2"]


def test_writer_does_not_mutate_model_species(tmp_path):
    map_ = _read(FIXTURE)
    species_before = len(map_.model.species)
    assert species_before == 2  # only s1, s2 — degraded species are layout-only

    out = tmp_path / "out.xml"
    _write(map_, str(out))
    assert len(map_.model.species) == species_before


def test_roundtrip_preserves_external_flags(tmp_path):
    map_ = _read(FIXTURE)
    out = tmp_path / "out.xml"
    _write(map_, str(out))
    map2 = _read(str(out))
    r1 = _reaction_by_id(map2, "R1")
    r2 = _reaction_by_id(map2, "R2")
    assert r1.has_external_source is True
    assert r2.has_external_sink is True


def test_roundtrip_preserves_degraded_layouts(tmp_path):
    map_ = _read(FIXTURE)
    out = tmp_path / "out.xml"
    _write(map_, str(out))
    map2 = _read(str(out))
    degraded = [
        le
        for le in map2.layout.layout_elements
        if isinstance(le, (DegradedLayout, DegradedActiveLayout))
    ]
    assert len(degraded) == 2


def test_output_xml_has_degraded_species(tmp_path):
    map_ = _read(FIXTURE)
    out = tmp_path / "out.xml"
    _write(map_, str(out))

    tree = lxml.etree.parse(str(out))
    root = tree.getroot()
    ns = {"sbml": _SBML_NS, "cd": _CD_NS}
    species_elements = root.findall(".//sbml:listOfSpecies/sbml:species", ns)
    degraded_count = 0
    for sp in species_elements:
        cls = sp.find(".//cd:speciesIdentity/cd:class", ns)
        if cls is not None and cls.text == "DEGRADED":
            degraded_count += 1
    assert degraded_count >= 2
