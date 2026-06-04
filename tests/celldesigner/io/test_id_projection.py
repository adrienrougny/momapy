"""Tests for CellDesigner XML-id projection (grammar, share, metaid).

See ``plans/writer_xml_id_projection.md``.
"""

import collections
import dataclasses
import os
import re

import pytest

import momapy.io.core
import momapy.celldesigner.io.celldesigner._writing as cd_writing
import momapy.celldesigner.io.celldesigner.writer as cd_writer
from momapy.celldesigner.layout import ModificationLayout
from momapy.celldesigner.layout import StructuralStateLayout

_SID = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_CD_MAPS_DIR = os.path.join(_TEST_DIR, "..", "maps")


@dataclasses.dataclass(frozen=True)
class _FakeElement:
    id_: str
    metaid: str | None = None


def _writing_context():
    return cd_writer.CellDesignerWritingContext(
        map_=None,
        element_to_annotations={},
        element_to_notes={},
        source_id_to_model_element=None,
        source_id_to_layout_element=None,
        with_annotations=True,
        with_notes=True,
    )


class TestEnsureSbmlSid:
    def test_uuid_is_projected_to_valid_sid(self):
        result = cd_writing.ensure_sbml_sid("89a50724-5240-4529-ae7a-179ae994ec38")
        assert _SID.match(result)
        assert "-" not in result

    def test_valid_sid_is_unchanged(self):
        assert cd_writing.ensure_sbml_sid("s_id_ne143") == "s_id_ne143"

    def test_empty_is_empty(self):
        assert cd_writing.ensure_sbml_sid("") == ""


class TestGetXmlId:
    def test_from_scratch_uuid_projects_to_valid_sid(self):
        ctx = _writing_context()
        result = cd_writer._get_xml_id(ctx, _FakeElement("89a50724-5240-ae7a"))
        assert _SID.match(result)

    def test_distinct_ids_projecting_equal_are_deduped(self):
        ctx = _writing_context()
        # Bind both objects so they stay alive: the memo is keyed by id().
        element_a = _FakeElement("a-b")
        element_b = _FakeElement("a_b")
        a = cd_writer._get_xml_id(ctx, element_a, share=False)
        b = cd_writer._get_xml_id(ctx, element_b, share=False)
        assert {a, b} == {"a_b", "a_b_1"}

    def test_share_true_collapses_same_candidate(self):
        # Two distinct objects with the same id_ name one entity -> one id.
        ctx = _writing_context()
        first = cd_writer._get_xml_id(ctx, _FakeElement("s_x"), share=True)
        second = cd_writer._get_xml_id(ctx, _FakeElement("s_x"), share=True)
        assert first == second == "s_x"

    def test_metaid_is_unique_per_emission(self):
        # share=False + memoize=False: one object emitted twice -> distinct ids.
        ctx = _writing_context()
        participant = _FakeElement("re_sp")
        first = cd_writer._get_xml_id(
            ctx, participant, candidate="re_sp", share=False, memoize=False
        )
        second = cd_writer._get_xml_id(
            ctx, participant, candidate="re_sp", share=False, memoize=False
        )
        assert {first, second} == {"re_sp", "re_sp_1"}


class TestGetSpeciesId:
    def test_strips_active_suffix(self):
        ctx = _writing_context()
        assert cd_writer._get_species_id(_FakeElement("s1_active"), ctx) == "s1"

    def test_active_and_inactive_share_one_species_id(self):
        ctx = _writing_context()
        inactive = cd_writer._get_species_id(_FakeElement("s1"), ctx)
        active = cd_writer._get_species_id(_FakeElement("s1_active"), ctx)
        assert inactive == active == "s1"

    def test_none_species_is_empty(self):
        ctx = _writing_context()
        assert cd_writer._get_species_id(None, ctx) == ""


def _cd_files():
    if not os.path.exists(_CD_MAPS_DIR):
        return []
    return [f for f in os.listdir(_CD_MAPS_DIR) if f.endswith(".xml")]


class TestRoundTripIds:
    @pytest.mark.slow
    @pytest.mark.parametrize("filename", _cd_files())
    def test_ids_valid_metaids_unique_refs_resolve(self, filename, tmp_path):
        result = momapy.io.core.read(os.path.join(_CD_MAPS_DIR, filename))
        out_file = tmp_path / filename
        momapy.io.core.write(result.obj, out_file, writer="celldesigner")
        text = out_file.read_text()
        # Every id / metaid is a valid SId.
        for attr in ("id", "metaid"):
            for value in re.findall(rf'\b{attr}="([^"]*)"', text):
                assert _SID.match(value), f"{attr}={value!r} is not a valid SId"
        # metaids are unique across the document (xsd:ID).
        metaids = re.findall(r'\bmetaid="([^"]*)"', text)
        dups = [m for m, c in collections.Counter(metaids).items() if c > 1]
        assert not dups, f"duplicate metaids: {dups[:8]}"
        # Every species reference resolves to a defined species id.
        defined = set(
            re.findall(r'<(?:celldesigner:)?species\b[^>]*\bid="([^"]*)"', text)
        )
        for ref in re.findall(r'\bspecies="([^"]*)"', text):
            assert ref in defined, f"species={ref!r} does not resolve"


def _walk_layout_elements(layout_element):
    """Yield a layout element and all of its descendants."""
    yield layout_element
    for child in getattr(layout_element, "layout_elements", None) or []:
        yield from _walk_layout_elements(child)


class TestModificationLayoutIdUniqueness:
    """Modification / structural-state layout ids must be unique even when
    one species appears under several aliases.

    The reader keys these child layout ids on the alias (the layout
    element), not the model species id: a species-id-based prefix would
    collide when the same species is reused across complexes/aliases.
    """

    @pytest.mark.parametrize("filename", _cd_files())
    def test_modification_layout_ids_are_unique(self, filename):
        result = momapy.io.core.read(os.path.join(_CD_MAPS_DIR, filename))
        layout = result.obj.layout
        if layout is None:
            pytest.skip("map has no layout")
        modification_ids = []
        structural_state_ids = []
        for top in layout.layout_elements:
            for element in _walk_layout_elements(top):
                if isinstance(element, ModificationLayout):
                    modification_ids.append(element.id_)
                elif isinstance(element, StructuralStateLayout):
                    structural_state_ids.append(element.id_)
        modification_dups = [
            id_
            for id_, count in collections.Counter(modification_ids).items()
            if count > 1
        ]
        structural_state_dups = [
            id_
            for id_, count in collections.Counter(structural_state_ids).items()
            if count > 1
        ]
        assert not modification_dups, (
            f"duplicate modification layout ids: {modification_dups[:8]}"
        )
        assert not structural_state_dups, (
            f"duplicate structural-state layout ids: {structural_state_dups[:8]}"
        )
