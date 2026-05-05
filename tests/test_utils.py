"""Tests for momapy.utils module."""

import pytest
import momapy.utils


class TestSurjectionDict:
    """Tests for SurjectionDict class."""

    def test_init_empty(self):
        """Test creating an empty SurjectionDict."""
        d = momapy.utils.SurjectionDict()
        assert len(d) == 0
        assert len(d.inverse) == 0

    def test_init_with_items(self):
        """Test creating SurjectionDict with initial items."""
        d = momapy.utils.SurjectionDict({"a": 1, "b": 2, "c": 1})
        assert d["a"] == 1
        assert d["b"] == 2
        assert d["c"] == 1
        assert 1 in d.inverse
        assert set(d.inverse[1]) == {"a", "c"}

    def test_setitem(self):
        """Test setting items."""
        d = momapy.utils.SurjectionDict()
        d["key1"] = "value1"
        assert d["key1"] == "value1"
        assert "value1" in d.inverse

    def test_delitem(self):
        """Test deleting items."""
        d = momapy.utils.SurjectionDict({"a": 1, "b": 2})
        del d["a"]
        assert "a" not in d
        assert 1 not in d.inverse

    def test_inverse_property(self):
        """Test inverse property."""
        d = momapy.utils.SurjectionDict({"a": 1, "b": 1, "c": 2})
        inverse = d.inverse
        assert 1 in inverse
        assert set(inverse[1]) == {"a", "b"}
        assert set(inverse[2]) == {"c"}


class TestFrozenSurjectionDict:
    """Tests for FrozenSurjectionDict class."""

    def test_init_empty(self):
        """Test creating an empty FrozenSurjectionDict."""
        d = momapy.utils.FrozenSurjectionDict()
        assert len(d) == 0
        assert len(d.inverse) == 0

    def test_init_with_items(self):
        """Test creating FrozenSurjectionDict with items."""
        d = momapy.utils.FrozenSurjectionDict({"a": 1, "b": 2, "c": 1})
        assert d["a"] == 1
        assert d["b"] == 2
        assert set(d.inverse[1]) == {"a", "c"}

    def test_immutable(self):
        """Test that FrozenSurjectionDict is immutable."""
        d = momapy.utils.FrozenSurjectionDict({"a": 1})
        with pytest.raises(Exception):  # frozendict raises TypeError or similar
            d["b"] = 2


class _Holder:
    """Hashable, ``==``-equal but id-distinct helper for identity tests."""

    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        return isinstance(other, _Holder) and self.label == other.label

    def __hash__(self):
        return hash(self.label)


class TestFrozenIdentitySurjectionDict:
    """Tests for FrozenIdentitySurjectionDict class."""

    def test_init_empty(self):
        d = momapy.utils.FrozenIdentitySurjectionDict()
        assert len(d) == 0
        assert d.inverse == {}

    def test_inverse_keyed_by_id_not_value(self):
        a = _Holder("x")
        b = _Holder("x")
        assert a == b and a is not b
        d = momapy.utils.FrozenIdentitySurjectionDict({"k1": a, "k2": b})
        assert d.inverse[id(a)] == {"k1"}
        assert d.inverse[id(b)] == {"k2"}
        assert id(a) != id(b)

    def test_multiple_keys_same_value(self):
        a = _Holder("only")
        d = momapy.utils.FrozenIdentitySurjectionDict({"k1": a, "k2": a})
        assert d.inverse[id(a)] == {"k1", "k2"}

    def test_forward_dict_uses_eq(self):
        """Forward-dict semantics are unchanged: ``==`` keys collide."""
        d = momapy.utils.FrozenIdentitySurjectionDict({"k": 1})
        assert d["k"] == 1

    def test_immutable(self):
        d = momapy.utils.FrozenIdentitySurjectionDict({"k": 1})
        with pytest.raises(Exception):
            d["other"] = 2

    def test_pickle_roundtrip_rebuilds_inverse(self):
        import pickle

        a = _Holder("x")
        b = _Holder("x")
        d = momapy.utils.FrozenIdentitySurjectionDict({"k1": a, "k2": b})
        loaded = pickle.loads(pickle.dumps(d))
        # Forward dict equal under ==, but underlying value identities are
        # fresh: the rebuilt inverse keys must match the loaded values'
        # id()s, not the originals'.
        loaded_a = loaded["k1"]
        loaded_b = loaded["k2"]
        assert loaded.inverse[id(loaded_a)] == {"k1"}
        assert loaded.inverse[id(loaded_b)] == {"k2"}


def test_get_element_from_collection():
    """Test get_element_from_collection function."""
    collection = [1, 2, 3, 4]
    assert momapy.utils.get_element_from_collection(2, collection) == 2
    assert momapy.utils.get_element_from_collection(5, collection) is None


def test_get_or_return_element_from_collection():
    """Test get_or_return_element_from_collection function."""
    collection = [1, 2, 3, 4]
    assert momapy.utils.get_or_return_element_from_collection(2, collection) == 2
    assert momapy.utils.get_or_return_element_from_collection(5, collection) == 5


def test_add_or_replace_element_in_set():
    """Test add_or_replace_element_in_set function."""
    s = {1, 2, 3}
    result = momapy.utils.add_or_replace_element_in_set(4, s)
    assert result == 4
    assert 4 in s

    # Test with existing element
    result = momapy.utils.add_or_replace_element_in_set(2, s)
    assert result == 2
    assert 2 in s


def test_make_uuid4_as_str():
    """Test make_uuid4_as_str function."""
    uuid1 = momapy.utils.make_uuid4_as_str()
    uuid2 = momapy.utils.make_uuid4_as_str()

    assert isinstance(uuid1, str)
    assert isinstance(uuid2, str)
    assert uuid1 != uuid2
    assert len(uuid1) == 36  # Standard UUID string length


class TestIdentityMultiDict:
    def test_add_and_get_one(self):
        d = momapy.utils.IdentityMultiDict()
        a = object()
        d.add("x", a)
        assert d.get_one("x") is a
        assert d.get_all("x") == frozenset({a})
        assert d.inverse[id(a)] == frozenset({"x"})

    def test_get_one_collision_raises(self):
        d = momapy.utils.IdentityMultiDict()
        a, b = object(), object()
        d.add("x", a)
        d.add("x", b)
        import pytest

        with pytest.raises(ValueError):
            d.get_one("x")
        assert d.get_all("x") == frozenset({a, b})

    def test_replace_value(self):
        d = momapy.utils.IdentityMultiDict()
        a, b, c = object(), object(), object()
        d.add("x", a)
        d.add("y", a)
        d.add("z", b)
        d.replace_value(a, c)
        assert d.get_one("x") is c
        assert d.get_one("y") is c
        assert d.get_one("z") is b
        assert d.inverse[id(c)] == frozenset({"x", "y"})
        assert id(a) not in d.inverse

    def test_replace_value_chained(self):
        """Two evictions under the same key collapse to a single survivor."""
        d = momapy.utils.IdentityMultiDict()
        a, b, c = object(), object(), object()
        d.add("k", a)
        d.replace_value(a, b)
        d.replace_value(b, c)
        assert d.get_one("k") is c
        assert d.inverse[id(c)] == frozenset({"k"})

    def test_remove(self):
        d = momapy.utils.IdentityMultiDict()
        a, b = object(), object()
        d.add("x", a)
        d.add("x", b)
        d.remove("x", a)
        assert d.get_all("x") == frozenset({b})
        assert id(a) not in d.inverse


class TestFrozenIdentityMultiDict:
    def test_construct_from_mapping(self):
        a, b = object(), object()
        d = momapy.utils.FrozenIdentityMultiDict({"x": [a, b], "y": [a]})
        assert d.get_all("x") == frozenset({a, b})
        assert d.get_one("y") is a
        assert d.inverse[id(a)] == frozenset({"x", "y"})
        assert d.inverse[id(b)] == frozenset({"x"})

    def test_get_one_collision_raises(self):
        a, b = object(), object()
        d = momapy.utils.FrozenIdentityMultiDict({"x": [a, b]})
        import pytest

        with pytest.raises(ValueError):
            d.get_one("x")
