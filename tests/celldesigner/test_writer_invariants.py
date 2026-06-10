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
from momapy.celldesigner.model import Complex


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
    for key in map_.layout_model_mapping.inverse.get(id(complex_), ()):
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
            for key in mapping.inverse.get(id(outer), ())
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
    """Identity-keyed mapping is authoritative for layout↔model pairing.

    Replacing a mapping value with a content-equal-but-id-distinct
    sibling no longer aliases the two: the layout pairs to the
    inserted instance by identity, and the original (still in the
    model graph) has no recorded layout. The writer's pairing oracle
    (``get_child_layout_elements``) therefore returns no layout for
    the in-scope subunit, and no alias is emitted. The pairing is
    consistent — model and mapping disagree only by identity, which
    Tier 2 surfaces precisely.
    """

    def test_writer_drops_alias_for_id_distinct_mapping_value(
        self, neuro_map, tmp_path
    ):
        target_complex, target_subunit, target_layout = (
            _find_complex_with_non_complex_subunit(neuro_map)
        )
        stale_subunit = dataclasses.replace(target_subunit, id_="STALE_ALTERNATE_ID")
        assert stale_subunit == target_subunit
        assert stale_subunit is not target_subunit
        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        target_layout_builder = cache[id(target_layout)]
        stale_subunit_builder = momapy.builder.builder_from_object(stale_subunit)
        map_builder.layout_model_mapping[target_layout_builder] = stale_subunit_builder
        new_map = momapy.builder.object_from_builder(map_builder)
        # Forward-dict lookup: ``==``-keyed by layout, value is the
        # inserted stale instance.
        assert (
            new_map.layout_model_mapping.get_mapping(target_layout).id_
            == "STALE_ALTERNATE_ID"
        )
        # Identity-keyed inverse: target_subunit's identity is not in
        # the mapping; only stale_subunit's is.
        mapping = new_map.layout_model_mapping
        assert mapping.inverse.get(id(target_subunit)) is None
        out_file = tmp_path / "stale.xml"
        momapy.io.core.write(new_map, out_file, writer="celldesigner")
        tree = lxml.etree.parse(str(out_file))
        aliases = tree.getroot().findall(
            f".//{{{_CD_NS}}}speciesAlias[@id='{target_layout.id_}']"
        )
        assert aliases == [], (
            "mapping is identity-keyed: target_layout pairs to the inserted "
            "stale instance, so target_subunit (still in the model) has no "
            "paired layout and no alias should be emitted"
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


class TestSubunitToComplexUsesIdentity:
    """Writer's ``subunit_to_complex`` index must key by identity.

    Model species use ``compare=False`` on ``id_``, so two distinct
    species objects can be content-equal. The writer's
    ``subunit_to_complex`` walk records, for each subunit reference,
    the ancestor complex it lives under. Lookups against this index
    must answer "is *this exact* species object a subunit?" — an
    identity question — not the looser "is some content-equal species
    a subunit?". A plain ``dict`` conflates the two and silently drops
    the top-level alias for any species content-equal to (but distinct
    from) a kept complex's subunit.
    """

    def test_top_level_alias_emitted_when_content_equal_to_subunit(
        self, neuro_map, tmp_path
    ):
        target_complex, target_subunit, _ = _find_complex_with_non_complex_subunit(
            neuro_map
        )
        duplicate_species = dataclasses.replace(
            target_subunit, id_="DUPLICATE_TOP_LEVEL"
        )
        assert duplicate_species == target_subunit
        assert duplicate_species is not target_subunit

        subunit_identities: set[int] = set()
        for sp in neuro_map.model.species:
            if isinstance(sp, Complex):
                for sub in sp.subunits:
                    subunit_identities.add(id(sub))
        chosen = None
        for sp in neuro_map.model.species:
            if isinstance(sp, Complex):
                continue
            if id(sp) in subunit_identities:
                continue
            layouts = [
                key
                for key in neuro_map.layout_model_mapping.inverse.get(id(sp), ())
                if not isinstance(key, frozenset)
            ]
            if layouts:
                chosen = (sp, layouts[0])
                break
        if chosen is None:
            pytest.skip("no non-subunit top-level species with singleton layout")
        _existing_top_species, existing_top_layout = chosen

        cache: dict = {}
        map_builder = momapy.builder.builder_from_object(
            neuro_map, object_to_builder=cache
        )
        existing_top_layout_builder = cache[id(existing_top_layout)]
        duplicate_builder = momapy.builder.builder_from_object(duplicate_species)
        map_builder.model.species.add(duplicate_builder)
        map_builder.layout_model_mapping[existing_top_layout_builder] = (
            duplicate_builder
        )
        new_map = momapy.builder.object_from_builder(map_builder)

        in_model_species = [
            sp for sp in new_map.model.species if sp == duplicate_species
        ]
        assert in_model_species, (
            "duplicate must be visible to the writer's model.species iteration"
        )

        out_file = tmp_path / "content_equal_duplicate.xml"
        momapy.io.core.write(new_map, out_file, writer="celldesigner")
        tree = lxml.etree.parse(str(out_file))
        aliases = tree.getroot().findall(
            f".//{{{_CD_NS}}}speciesAlias[@id='{existing_top_layout.id_}']"
        )
        assert len(aliases) == 1, (
            "writer must emit a speciesAlias for the top-level species's "
            "layout even though its model species is content-equal to a "
            "subunit of a kept complex"
        )
