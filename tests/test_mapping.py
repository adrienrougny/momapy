"""Tests for momapy.core.mapping module."""

import dataclasses
import pytest

import momapy.core.elements
import momapy.core.mapping
import momapy.geometry
import momapy.drawing


# ---------------------------------------------------------------------------
# Minimal concrete helpers
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LayoutElem(momapy.core.elements.LayoutElement):
    """Minimal concrete LayoutElement for testing."""

    name: str = ""

    def bbox(self):
        return momapy.geometry.Bbox(momapy.geometry.Point(0, 0), 1, 1)

    def drawing_elements(self):
        return []

    def children(self):
        return []

    def childless(self):
        return self


def _le(name: str) -> _LayoutElem:
    """Shorthand to create a named layout element."""
    return _LayoutElem(name=name)


def _me() -> momapy.core.elements.ModelElement:
    """Shorthand to create a model element."""
    return momapy.core.elements.ModelElement()


# ---------------------------------------------------------------------------
# LayoutModelMappingBuilder — add_mapping / _singleton_to_key
# ---------------------------------------------------------------------------


class TestAddMapping:
    def test_simple_add(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        assert builder[le1] is me1

    def test_no_anchor_without_anchor_arg(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        assert len(builder._singleton_to_key) == 0

    def test_anchor_populates_singleton_to_key(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        assert builder._singleton_to_key[le1] is key

    def test_anchor_does_not_pollute_other_keys(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, le3, me1, me2 = _le("1"), _le("2"), _le("3"), _me(), _me()
        key1 = frozenset([le1, le2])
        builder.add_mapping(key1, me1, anchor=le1)
        builder.add_mapping(le3, me2)
        assert le3 not in builder._singleton_to_key

    def test_replace_remaps_existing(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        builder.add_mapping(le1, me1)
        builder.add_mapping(le2, me1, replace=True)
        # After replace, le1 still maps to me1 (re-mapped) and le2 also maps
        assert builder[le1] is me1
        assert builder[le2] is me1


# ---------------------------------------------------------------------------
# LayoutModelMappingBuilder.build()
# ---------------------------------------------------------------------------


class TestBuild:
    def test_basic_build(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        mapping = builder.build()
        assert isinstance(mapping, momapy.core.mapping.LayoutModelMapping)
        assert mapping[le1] is me1

    def test_singleton_to_key_transferred(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()
        assert mapping._singleton_to_key[le1] == key

    def test_singleton_to_key_empty_when_not_set(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        mapping = builder.build()
        assert len(mapping._singleton_to_key) == 0

    def test_singleton_to_key_is_frozendict(self):
        import frozendict

        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()
        assert isinstance(mapping._singleton_to_key, frozendict.frozendict)


# ---------------------------------------------------------------------------
# LayoutModelMapping.get_mapping()
# ---------------------------------------------------------------------------


class TestGetMapping:
    @pytest.fixture
    def simple_mapping(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        return builder.build(), le1, me1

    def test_direct_key_lookup(self, simple_mapping):
        mapping, le1, me1 = simple_mapping
        assert mapping.get_mapping(le1) is me1

    def test_inverse_lookup(self, simple_mapping):
        mapping, le1, me1 = simple_mapping
        result = mapping.get_mapping(me1)
        assert result is not None
        assert le1 in result

    def test_returns_none_for_unknown(self, simple_mapping):
        mapping, _, _ = simple_mapping
        assert mapping.get_mapping(_le("unknown")) is None

    def test_frozenset_key_direct_lookup(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()
        assert mapping.get_mapping(key) is me1

    def test_singleton_fallback_resolves_model_element(self):
        """get_mapping(anchor) should return the model element via _singleton_to_key."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()
        assert mapping.get_mapping(le1) is me1

    def test_non_anchor_member_not_in_singleton_to_key(self):
        """The non-anchor member of a frozenset should NOT resolve via _singleton_to_key."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()
        # le2 is not the anchor and not a direct key, so inverse should be used
        result = mapping.get_mapping(le2)
        # le2 is not a key itself, not a model element — should be None
        assert result is None

    def test_multi_frozenset_anchor_resolves_correct_element(self):
        """An element in two frozensets resolves via the one it was registered for."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le_op, le_src, le_tgt, le_proc = _le("op"), _le("src"), _le("tgt"), _le("proc")
        me_op, me_mod = _me(), _me()

        # le_op is anchor of operator frozenset → me_op
        op_key = frozenset([le_op, le_proc])
        builder.add_mapping(op_key, me_op, anchor=le_op)

        # le_op also appears in a modulation frozenset, but NOT as anchor
        mod_key = frozenset([le_op, le_src, le_tgt])
        builder.add_mapping(mod_key, me_mod)

        mapping = builder.build()

        # get_mapping(le_op) must return me_op (via _singleton_to_key), not me_mod
        assert mapping.get_mapping(le_op) is me_op

    def test_multiple_anchors_independent(self):
        """Two different anchors each resolve to their respective model elements."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, le3, le4 = _le("1"), _le("2"), _le("3"), _le("4")
        me1, me2 = _me(), _me()

        key1 = frozenset([le1, le2])
        key2 = frozenset([le3, le4])
        builder.add_mapping(key1, me1, anchor=le1)
        builder.add_mapping(key2, me2, anchor=le3)

        mapping = builder.build()
        assert mapping.get_mapping(le1) is me1
        assert mapping.get_mapping(le3) is me2


# ---------------------------------------------------------------------------
# LayoutModelMappingBuilder.get_mapping()
# ---------------------------------------------------------------------------


class TestBuilderGetMapping:
    def test_direct_key(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        assert builder.get_mapping(le1) is me1

    def test_inverse(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        result = builder.get_mapping(me1)
        assert le1 in result


# ---------------------------------------------------------------------------
# LayoutModelMappingBuilder.from_object() round-trip
# ---------------------------------------------------------------------------


class TestFromObjectRoundtrip:
    def test_simple_roundtrip(self):
        """build → from_object → build preserves the key in the mapping."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        mapping = builder.build()
        builder2 = momapy.core.mapping.LayoutModelMappingBuilder.from_object(mapping)
        mapping2 = builder2.build()
        # Round-trip rebuilds equal-but-not-identical instances; le1 must be a key.
        assert le1 in mapping2

    def test_singleton_to_key_preserved_through_roundtrip(self):
        """from_object → build preserves _singleton_to_key entries."""
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, le2, me1 = _le("le1"), _le("le2"), _me()
        key = frozenset([le1, le2])
        builder.add_mapping(key, me1, anchor=le1)
        mapping = builder.build()

        builder2 = momapy.core.mapping.LayoutModelMappingBuilder.from_object(mapping)
        mapping2 = builder2.build()

        # The anchor must be recorded and resolve to a model element.
        assert le1 in mapping2._singleton_to_key
        assert mapping2.get_mapping(le1) is not None


# ---------------------------------------------------------------------------
# LayoutModelMapping.is_submapping()
# ---------------------------------------------------------------------------


class TestIsSubmapping:
    def test_empty_is_submapping_of_anything(self):
        empty = momapy.core.mapping.LayoutModelMappingBuilder().build()
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        full = builder.build()
        assert empty.is_submapping(full)

    def test_identical_is_submapping(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        mapping = builder.build()
        assert mapping.is_submapping(mapping)

    def test_superset_is_not_submapping(self):
        builder = momapy.core.mapping.LayoutModelMappingBuilder()
        le1, me1 = _le("le1"), _me()
        builder.add_mapping(le1, me1)
        full = builder.build()
        empty = momapy.core.mapping.LayoutModelMappingBuilder().build()
        assert not full.is_submapping(empty)
