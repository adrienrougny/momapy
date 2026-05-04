"""Tests for CellDesigner writer model-walk invariants.

See ``plans/writer_model_walk_emission.md``. The writer must source
every model-side identifier emitted into XML from a model element in
scope on the model walk, never from a value-keyed lookup into the
layout-model mapping. The mapping is consulted only as a pairing
oracle.
"""

import dataclasses
import os

import lxml.etree
import pytest

import momapy.builder
import momapy.io.core
from momapy.celldesigner.layout import GenericProteinLayout
from momapy.celldesigner.model import Complex
from momapy.geometry import Point


_CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_CD_MAPS_DIR = os.path.join(_TEST_DIR, "maps")
_NEUROINFLAMMATION = os.path.join(_CD_MAPS_DIR, "Neuroinflammation.xml")


@pytest.fixture
def neuro_map():
    if not os.path.exists(_NEUROINFLAMMATION):
        pytest.skip("Neuroinflammation fixture not available")
    return momapy.io.core.read(_NEUROINFLAMMATION).obj


def _find_complex_with_non_complex_subunit(map_):
    """Return the first ``(complex, subunit, subunit_layout)`` triple where
    ``subunit`` is a non-Complex Species and a layout is recorded under
    ``complex`` for it."""
    mapping = map_.layout_model_mapping
    for species in map_.model.species:
        if not isinstance(species, Complex):
            continue
        for subunit in species.subunits:
            if isinstance(subunit, Complex):
                continue
            layouts = mapping.get_child_layout_elements(subunit, species)
            if layouts:
                return species, subunit, layouts[0]
    raise RuntimeError("no complex with non-complex subunit and recorded layout found")


def _find_outer_layout(map_, complex_):
    for key in map_.layout_model_mapping.inverse.get(complex_, []):
        if not isinstance(key, frozenset):
            return key
    raise RuntimeError(f"no singleton layout for complex {complex_.id_}")


def _find_nested_complex_pair(map_):
    """Return ``(outer_complex, outer_layout, inner_complex, inner_layout)``."""
    mapping = map_.layout_model_mapping
    for outer in map_.model.species:
        if not isinstance(outer, Complex):
            continue
        outer_layouts = [
            key
            for key in mapping.inverse.get(outer, [])
            if not isinstance(key, frozenset)
        ]
        if not outer_layouts:
            continue
        for inner in outer.subunits:
            if not isinstance(inner, Complex):
                continue
            inner_layouts = mapping.get_child_layout_elements(inner, outer)
            if inner_layouts:
                return outer, outer_layouts[0], inner, inner_layouts[0]
    raise RuntimeError("no nested complex with mapped layouts found")


class TestStaleMappingSurvivesWriting:
    """Writer uses the model walk's identity, not the layout-model
    mapping's stored value, when emitting subunit aliases.

    Model dataclasses set ``compare=False`` on ``id_``, so a content-
    equal copy with a different ``id_`` is ``__eq__`` to the original
    and the value-keyed mapping treats them as the same key. Replacing
    the mapping value simulates an upstream construction artefact where
    the mapping holds a content-equal-but-id-distinct sibling.
    """

    def test_writer_emits_model_walk_subunit_id(self, neuro_map, tmp_path):
        target_complex, target_subunit, target_layout = (
            _find_complex_with_non_complex_subunit(neuro_map)
        )
        stale_subunit = dataclasses.replace(target_subunit, id_="STALE_ALTERNATE_ID")
        assert stale_subunit == target_subunit
        assert stale_subunit.id_ != target_subunit.id_
        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        target_layout_builder = cache[id(target_layout)]
        stale_subunit_builder = momapy.builder.builder_from_object(stale_subunit)
        map_builder.layout_model_mapping[target_layout_builder] = stale_subunit_builder
        new_map = momapy.builder.object_from_builder(map_builder)
        assert (
            new_map.layout_model_mapping.get_mapping(target_layout).id_
            == "STALE_ALTERNATE_ID"
        )
        out_file = tmp_path / "stale.xml"
        momapy.io.core.write(new_map, out_file, writer="celldesigner")
        tree = lxml.etree.parse(str(out_file))
        aliases = tree.getroot().findall(
            f".//{{{_CD_NS}}}speciesAlias[@id='{target_layout.id_}']"
        )
        assert len(aliases) == 1
        assert aliases[0].get("species") == target_subunit.id_, (
            "writer used the mapping's stale value instead of the "
            "model walk's in-scope subunit"
        )

    def test_round_trip_succeeds_with_stale_mapping(self, neuro_map, tmp_path):
        target_complex, target_subunit, target_layout = (
            _find_complex_with_non_complex_subunit(neuro_map)
        )
        stale_subunit = dataclasses.replace(target_subunit, id_="STALE_ALTERNATE_ID_2")
        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        target_layout_builder = cache[id(target_layout)]
        stale_subunit_builder = momapy.builder.builder_from_object(stale_subunit)
        map_builder.layout_model_mapping[target_layout_builder] = stale_subunit_builder
        new_map = momapy.builder.object_from_builder(map_builder)
        out_file = tmp_path / "stale_roundtrip.xml"
        momapy.io.core.write(new_map, out_file, writer="celldesigner")
        result = momapy.io.core.read(str(out_file), reader="celldesigner")
        assert result.obj is not None


class TestMappingMissRaises:
    """A subunit-bearing layout under a complex layout with no mapping
    entry triggers a pre-emission ValueError naming the layout id."""

    def test_unmapped_complex_child_raises(self, neuro_map, tmp_path):
        target_complex, _, _ = _find_complex_with_non_complex_subunit(neuro_map)
        outer_layout = _find_outer_layout(neuro_map, target_complex)
        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        outer_layout_builder = cache[id(outer_layout)]
        stray_layout_builder = momapy.builder.new_builder_object(GenericProteinLayout)
        stray_layout_builder.position = Point(0.0, 0.0)
        stray_layout_builder.width = 30.0
        stray_layout_builder.height = 20.0
        stray_layout_builder.id_ = "STRAY_UNMAPPED_LAYOUT"
        outer_layout_builder.layout_elements.append(stray_layout_builder)
        new_map = momapy.builder.object_from_builder(map_builder)
        out_file = tmp_path / "miss.xml"
        with pytest.raises(ValueError, match="STRAY_UNMAPPED_LAYOUT"):
            momapy.io.core.write(new_map, out_file, writer="celldesigner")


class TestModelMappingDisagreementRaises:
    """A layout under a complex layout that maps to a model element not
    in the parent complex's ``subunits`` triggers a ValueError."""

    def test_layout_mapped_to_non_subunit_raises(self, neuro_map, tmp_path):
        target_complex, target_subunit, target_layout = (
            _find_complex_with_non_complex_subunit(neuro_map)
        )
        unrelated_species = None
        for species in neuro_map.model.species:
            if isinstance(species, Complex):
                continue
            if any(species == sub for sub in target_complex.subunits):
                continue
            unrelated_species = species
            break
        assert unrelated_species is not None
        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        target_layout_builder = cache[id(target_layout)]
        unrelated_builder = cache[id(unrelated_species)]
        map_builder.layout_model_mapping[target_layout_builder] = unrelated_builder
        new_map = momapy.builder.object_from_builder(map_builder)
        out_file = tmp_path / "disagree.xml"
        with pytest.raises(ValueError, match="not a subunit"):
            momapy.io.core.write(new_map, out_file, writer="celldesigner")


class TestNestedComplexAliasChaining:
    """Nested ``<complexSpeciesAlias>`` entries reference the outer
    complex's emitted alias id via ``complexSpeciesAlias``."""

    def test_inner_alias_references_outer(self, neuro_map, tmp_path):
        outer_complex, outer_layout, inner_complex, inner_layout = (
            _find_nested_complex_pair(neuro_map)
        )
        out_file = tmp_path / "nested.xml"
        momapy.io.core.write(neuro_map, out_file, writer="celldesigner")
        tree = lxml.etree.parse(str(out_file))
        nested_aliases = tree.getroot().findall(
            f".//{{{_CD_NS}}}complexSpeciesAlias[@id='{inner_layout.id_}']"
        )
        assert len(nested_aliases) == 1
        assert nested_aliases[0].get("complexSpeciesAlias") == outer_layout.id_
