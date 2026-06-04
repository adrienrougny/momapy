"""Tests for the shared XML-id uniqueness helper.

See ``plans/writer_xml_id_projection.md``.
"""

import momapy.io.utils


class TestMakeUniqueXmlId:
    def test_free_candidate_returned_as_is(self):
        used = set()
        assert momapy.io.utils.make_unique_xml_id("a", used) == "a"
        assert "a" in used

    def test_taken_candidate_is_suffixed(self):
        used = {"a"}
        assert momapy.io.utils.make_unique_xml_id("a", used) == "a_1"
        assert used == {"a", "a_1"}

    def test_repeated_calls_increment_suffix(self):
        used = set()
        results = [momapy.io.utils.make_unique_xml_id("x", used) for _ in range(3)]
        assert results == ["x", "x_1", "x_2"]

    def test_does_not_sanitise(self):
        # Grammar projection is the caller's job; the helper only dedupes.
        used = set()
        assert momapy.io.utils.make_unique_xml_id("a-b", used) == "a-b"
