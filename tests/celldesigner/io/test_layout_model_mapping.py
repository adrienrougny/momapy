"""Tests for layout_model_mapping integrity in CellDesigner reader."""

import pytest
import os
import dataclasses

import momapy.io.core
import momapy.celldesigner.map
import momapy.core.layout
import momapy.core.mapping

pytestmark = pytest.mark.slow

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CELLDESIGNER_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps")


def get_celldesigner_files():
    if not os.path.exists(CELLDESIGNER_MAPS_DIR):
        return []
    return [f for f in os.listdir(CELLDESIGNER_MAPS_DIR) if f.endswith(".xml")]


CELLDESIGNER_FILES = get_celldesigner_files()


def _collect_all_model_elements(obj, visited=None):
    """Recursively collect all dataclass objects reachable from a model."""
    if visited is None:
        visited = set()
    if id(obj) in visited:
        return visited
    visited.add(id(obj))
    result = set()
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        result.add(obj)
        for field in dataclasses.fields(type(obj)):
            value = getattr(obj, field.name)
            if isinstance(value, frozenset):
                for element in value:
                    result.update(_collect_all_model_elements(element, visited))
            elif dataclasses.is_dataclass(value) and not isinstance(value, type):
                result.update(_collect_all_model_elements(value, visited))
    return result


@pytest.fixture(scope="module", params=CELLDESIGNER_FILES)
def cd_map(request):
    path = os.path.join(CELLDESIGNER_MAPS_DIR, request.param)
    result = momapy.io.core.read(path)
    return result.obj


class TestLayoutModelMappingIntegrity:
    """Verify layout_model_mapping consistency after reading."""

    def test_mapping_is_not_none(self, cd_map):
        assert cd_map.layout_model_mapping is not None

    def test_every_node_layout_is_mapped(self, cd_map):
        """Every node layout element should appear in the mapping."""
        mapping = cd_map.layout_model_mapping
        for layout_element in cd_map.layout.layout_elements:
            if isinstance(layout_element, momapy.core.layout.Node):
                found = False
                if layout_element in mapping:
                    found = True
                else:
                    for key in mapping:
                        if isinstance(key, frozenset) and layout_element in key:
                            found = True
                            break
                assert found, (
                    f"{type(layout_element).__name__}({layout_element.id_}) "
                    f"not found in layout_model_mapping"
                )

    def test_mapping_values_reference_live_model_elements(self, cd_map):
        """Mapping values should reference elements in the model, not stale copies."""
        mapping = cd_map.layout_model_mapping
        all_model_elements = _collect_all_model_elements(cd_map.model)
        for layout_key, model_value in mapping.items():
            if isinstance(model_value, tuple):
                for element in model_value:
                    assert element in all_model_elements, (
                        f"Stale reference: {type(element).__name__}({element.id_}) "
                        f"not in model collections"
                    )
            else:
                assert model_value in all_model_elements, (
                    f"Stale reference: {type(model_value).__name__}({model_value.id_}) "
                    f"not in model collections"
                )

    def test_child_mappings_reference_parent(self, cd_map):
        """Child mappings (tuples) should have a parent that is itself mapped."""
        mapping = cd_map.layout_model_mapping
        all_mapped_model_elements = set()
        for model_value in mapping.values():
            if isinstance(model_value, tuple):
                for element in model_value:
                    all_mapped_model_elements.add(element)
            else:
                all_mapped_model_elements.add(model_value)
        for layout_key, model_value in mapping.items():
            if isinstance(model_value, tuple) and len(model_value) >= 2:
                parent = model_value[-1]
                assert parent in all_mapped_model_elements, (
                    f"Parent {type(parent).__name__}({parent.id_}) "
                    f"referenced in child mapping but not itself mapped"
                )


class TestFrozensetMappings:
    """Verify frozenset mapping keys for reactions and modulations."""

    def test_every_reaction_is_mapped_via_frozenset(self, cd_map):
        """Each reaction should be mapped via a frozenset key."""
        mapping = cd_map.layout_model_mapping
        for reaction in cd_map.model.reactions:
            found_key = None
            for key, value in mapping.items():
                if isinstance(key, frozenset) and value is reaction:
                    found_key = key
                    break
            assert found_key is not None, (
                f"Reaction {reaction.id_} not mapped via frozenset key"
            )
            assert len(found_key) > 1, (
                f"Reaction {reaction.id_} frozenset has only "
                f"{len(found_key)} element(s)"
            )

    def test_reaction_singleton_to_key_has_anchor(self, cd_map):
        """Each reaction frozenset should have exactly one anchor in
        _singleton_to_key that resolves back to it."""
        mapping = cd_map.layout_model_mapping
        for reaction in cd_map.model.reactions:
            frozenset_key = None
            for key, value in mapping.items():
                if isinstance(key, frozenset) and value is reaction:
                    frozenset_key = key
                    break
            if frozenset_key is None:
                continue
            anchors = [
                el
                for el in frozenset_key
                if mapping._singleton_to_key.get(el) == frozenset_key
            ]
            assert len(anchors) == 1, (
                f"Reaction {reaction.id_} frozenset should have exactly 1 "
                f"anchor in _singleton_to_key, found {len(anchors)}"
            )

    def test_reaction_participants_mapped_as_children(self, cd_map):
        """Each consumption/production arc should be mapped as
        (participant_model, reaction_model) tuple."""
        mapping = cd_map.layout_model_mapping
        for reaction in cd_map.model.reactions:
            frozenset_key = None
            for key, value in mapping.items():
                if isinstance(key, frozenset) and value is reaction:
                    frozenset_key = key
                    break
            if frozenset_key is None:
                continue
            arcs_in_frozenset = [
                el for el in frozenset_key if isinstance(el, momapy.core.layout.Arc)
            ]
            for arc in arcs_in_frozenset:
                if arc not in mapping:
                    continue
                arc_value = mapping[arc]
                assert isinstance(arc_value, tuple), (
                    f"Participant arc {type(arc).__name__} mapped to "
                    f"{type(arc_value).__name__}, expected tuple"
                )
                assert arc_value[1] is reaction, (
                    f"Participant arc parent is "
                    f"{type(arc_value[1]).__name__}({arc_value[1].id_}), "
                    f"expected reaction {reaction.id_}"
                )

    def test_every_modulation_is_mapped_via_frozenset(self, cd_map):
        """Each modulation should be mapped via a frozenset key."""
        mapping = cd_map.layout_model_mapping
        for modulation in cd_map.model.modulations:
            found_key = None
            for key, value in mapping.items():
                if isinstance(key, frozenset) and value is modulation:
                    found_key = key
                    break
            assert found_key is not None, (
                f"Modulation {modulation.id_} not mapped via frozenset key"
            )
            assert len(found_key) >= 3, (
                f"Modulation {modulation.id_} frozenset has only "
                f"{len(found_key)} elements, expected >= 3 "
                f"(arc + source + target)"
            )

    def test_modulation_singleton_to_key_has_anchor(self, cd_map):
        """Each modulation frozenset should have exactly one anchor in
        _singleton_to_key that resolves back to it."""
        mapping = cd_map.layout_model_mapping
        for modulation in cd_map.model.modulations:
            frozenset_key = None
            for key, value in mapping.items():
                if isinstance(key, frozenset) and value is modulation:
                    frozenset_key = key
                    break
            if frozenset_key is None:
                continue
            anchors = [
                el
                for el in frozenset_key
                if mapping._singleton_to_key.get(el) == frozenset_key
            ]
            assert len(anchors) == 1, (
                f"Modulation {modulation.id_} frozenset should have exactly "
                f"1 anchor in _singleton_to_key, found {len(anchors)}"
            )
