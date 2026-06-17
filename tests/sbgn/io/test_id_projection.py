"""Tests for SBGN-ML XML-id projection (grammar, uniqueness, consistency).

See ``plans/writer_xml_id_projection.md``.
"""

import dataclasses
import os
import re

import pytest

import momapy.io.core
import momapy.io.utils
import momapy.sbgn.io.sbgnml._writing as sbgn_writing
import momapy.sbgn.io.sbgnml.writer as sbgn_writer
import momapy.utils

_NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_SBGN_MAPS_DIR = os.path.join(_TEST_DIR, "..", "maps", "pd")
_ID_ATTR = re.compile(r'\b(?:id|source|target|compartmentRef)="([^"]*)"')


@dataclasses.dataclass(frozen=True)
class _FakeElement:
    id_: str


def _writing_context(source_id_to_layout_element=None):
    return momapy.io.utils.WritingContext(
        map_=None,
        element_to_annotations={},
        element_to_notes={},
        source_id_to_model_element=None,
        source_id_to_layout_element=source_id_to_layout_element,
        source_id_to_annotations=None,
        source_id_to_notes=None,
        with_annotations=True,
        with_notes=True,
    )


class TestEnsureNcname:
    def test_uuid_leading_digit_is_prefixed(self):
        result = sbgn_writing.ensure_ncname("9a50724-5240-4529")
        assert _NCNAME.match(result)
        assert result == "_9a50724-5240-4529"

    def test_letter_leading_uuid_keeps_hyphens(self):
        # Hyphens are valid in NCName, so a letter-leading UUID is unchanged.
        uuid = "a9a50724-5240-4529-ae7a-179ae994ec38"
        assert sbgn_writing.ensure_ncname(uuid) == uuid

    def test_colon_is_replaced(self):
        result = sbgn_writing.ensure_ncname("foo:bar")
        assert ":" not in result
        assert result == "foo_bar"

    def test_valid_ncname_is_unchanged(self):
        assert sbgn_writing.ensure_ncname("glyph1.2-3") == "glyph1.2-3"

    def test_empty_is_empty(self):
        assert sbgn_writing.ensure_ncname("") == ""


class TestGetXmlId:
    def test_from_scratch_uuid_projects_to_valid_ncname(self):
        ctx = _writing_context()
        element = _FakeElement("89a50724-5240-4529-ae7a-179ae994ec38")
        result = sbgn_writer._get_xml_id(ctx, element)
        assert _NCNAME.match(result)

    def test_same_element_is_stable(self):
        ctx = _writing_context()
        element = _FakeElement("9x")
        first = sbgn_writer._get_xml_id(ctx, element)
        assert sbgn_writer._get_xml_id(ctx, element) == first

    def test_distinct_elements_projecting_equal_are_deduped(self):
        ctx = _writing_context()
        # Both project to "foo_x" (colon coerced); must stay distinct.
        # Bind both objects so they stay alive: the memo is keyed by id().
        element_a = _FakeElement("foo:x")
        element_b = _FakeElement("foo_x")
        a = sbgn_writer._get_xml_id(ctx, element_a)
        b = sbgn_writer._get_xml_id(ctx, element_b)
        assert {a, b} == {"foo_x", "foo_x_1"}

    def test_reserved_source_id_is_kept_verbatim(self):
        good = _FakeElement("glyph1")
        bad = _FakeElement("9bad")
        source_map = momapy.utils.FrozenSurjectionDict({"glyph1": good, "9bad": bad})
        ctx = _writing_context(source_map)
        sbgn_writer._reserve_source_xml_ids(ctx)
        assert sbgn_writer._get_xml_id(ctx, good) == "glyph1"
        # Invalid source id was not reserved; it gets projected on demand.
        assert _NCNAME.match(sbgn_writer._get_xml_id(ctx, bad))


def _sbgn_files():
    if not os.path.exists(_SBGN_MAPS_DIR):
        return []
    return [f for f in os.listdir(_SBGN_MAPS_DIR) if f.endswith(".sbgn")]


class TestRoundTripIds:
    @pytest.mark.slow
    @pytest.mark.parametrize("filename", _sbgn_files())
    def test_emitted_ids_are_valid_and_unique(self, filename, tmp_path):
        result = momapy.io.core.read(os.path.join(_SBGN_MAPS_DIR, filename))
        out_file = tmp_path / filename
        momapy.io.core.write(result.obj, out_file, writer="sbgnml-0.3")
        text = out_file.read_text()
        glyph_arc_ids = re.findall(r'<(?:glyph|arc)\b[^>]*\bid="([^"]*)"', text)
        # Every emitted id is a valid NCName.
        for id_ in _ID_ATTR.findall(text):
            assert _NCNAME.match(id_), f"{id_!r} is not a valid NCName"
        # Glyph/arc ids are unique within the document.
        assert len(glyph_arc_ids) == len(set(glyph_arc_ids))
        # Every source/target/compartmentRef resolves to a defined id.
        port_ids = set(re.findall(r'<port\b[^>]*\bid="([^"]*)"', text))
        defined = set(glyph_arc_ids) | port_ids
        for attr in ("source", "target", "compartmentRef"):
            for ref in re.findall(rf'\b{attr}="([^"]*)"', text):
                assert ref in defined, f"{attr}={ref!r} does not resolve"
