"""Negative modulations are classified from their target, not the XML string.

CellDesigner writes a freshly drawn inhibition onto a phenotype as
``INHIBITION``, then rewrites it to ``NEGATIVE_INFLUENCE`` the next time the
file is saved.  Both spellings therefore name the same arc, and the reader
normalizes them against the target: ``Inhibition`` for a phenotype target,
``NegativeInfluence`` otherwise.

``fixtures/inhibition_phenotype.xml`` holds one protein X (s1), one phenotype
"apoptosis" (s2) and one protein Y (s3), wired as four modulations:

===== ==================== ============== =====================
id    reactionType         arc            expected class
===== ==================== ============== =====================
re1   INHIBITION           X -> apoptosis Inhibition
re2   NEGATIVE_INFLUENCE   Y -> apoptosis Inhibition
re3   NEGATIVE_INFLUENCE   apoptosis -> X NegativeInfluence
re4   INHIBITION           apoptosis -> Y NegativeInfluence
===== ==================== ============== =====================

re3 and re4 have a phenotype *source*, which must not affect the class.
"""

import os

import pytest

import momapy.io.core
from momapy.celldesigner.io.celldesigner._reading_classification import (
    normalize_modulation_class,
)
from momapy.celldesigner.io.celldesigner._writing import get_modulation_reaction_type
from momapy.celldesigner.model import Inhibition
from momapy.celldesigner.model import NegativeInfluence
from momapy.celldesigner.model import Phenotype
from momapy.celldesigner.model import UnknownInhibition
from momapy.celldesigner.model import UnknownNegativeInfluence


_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_FIXTURE = os.path.join(_TEST_DIR, "fixtures", "inhibition_phenotype.xml")

_EXPECTED_CLASSES = {
    "re1": Inhibition,
    "re2": Inhibition,
    "re3": NegativeInfluence,
    "re4": NegativeInfluence,
}


def _modulations_by_id(map_):
    return {modulation.id_: modulation for modulation in map_.model.modulations}


@pytest.fixture(scope="module")
def map_():
    return momapy.io.core.read(_FIXTURE).obj


@pytest.mark.parametrize("modulation_id", sorted(_EXPECTED_CLASSES))
def test_class_follows_the_target(map_, modulation_id):
    modulation = _modulations_by_id(map_)[modulation_id]
    assert type(modulation) is _EXPECTED_CLASSES[modulation_id]


@pytest.mark.parametrize("modulation_id", sorted(_EXPECTED_CLASSES))
def test_inhibition_exactly_when_target_is_a_phenotype(map_, modulation_id):
    modulation = _modulations_by_id(map_)[modulation_id]
    assert isinstance(modulation, Inhibition) is isinstance(
        modulation.target, Phenotype
    )


def test_roundtrip_preserves_the_classes(map_, tmp_path):
    output_file = tmp_path / "inhibition_phenotype.xml"
    momapy.io.core.write(map_, str(output_file), writer="celldesigner")
    reread = momapy.io.core.read(str(output_file)).obj
    assert reread.model.modulations == map_.model.modulations


@pytest.mark.parametrize(
    ("reaction_type", "expected_class_name"),
    [
        ("UNKNOWN_MODULATION", "UnknownModulation"),
        ("UNKNOWN_PHYSICAL_STIMULATION", "UnknownPhysicalStimulation"),
        ("UNKNOWN_TRIGGER", "UnknownTriggering"),
    ],
)
def test_non_reduced_unknown_types_are_readable(
    tmp_path, reaction_type, expected_class_name
):
    """The writer emits these for a phenotype target; reading them once raised.

    ``get_modulation_reaction_type`` returns the non-reduced spelling when the
    target is a phenotype, but ``KEY_TO_CLASS`` only carried the
    ``UNKNOWN_REDUCED_*`` keys, so re-reading momapy's own output raised
    `KeyError`.
    """
    with open(_FIXTURE) as fixture_file:
        source = fixture_file.read()
    input_file = tmp_path / f"{reaction_type.lower()}.xml"
    input_file.write_text(source.replace(">INHIBITION<", f">{reaction_type}<"))
    map_ = momapy.io.core.read(str(input_file)).obj
    class_names = {type(modulation).__name__ for modulation in map_.model.modulations}
    assert expected_class_name in class_names


class TestReaderWriterAreInverse:
    """`normalize_modulation_class` must undo `get_modulation_reaction_type`."""

    @pytest.mark.parametrize(
        "model_element_cls",
        [Inhibition, NegativeInfluence, UnknownInhibition, UnknownNegativeInfluence],
    )
    @pytest.mark.parametrize("target_is_a_phenotype", [True, False])
    def test_normalizing_is_a_fixed_point(
        self, map_, model_element_cls, target_is_a_phenotype
    ):
        modulations = _modulations_by_id(map_)
        target = (
            modulations["re1"].target
            if target_is_a_phenotype
            else modulations["re3"].target
        )
        assert isinstance(target, Phenotype) is target_is_a_phenotype
        normalized = normalize_modulation_class(model_element_cls, target)
        assert normalize_modulation_class(normalized, target) is normalized

    @pytest.mark.parametrize(
        ("model_element_cls", "target_is_a_phenotype", "expected_reaction_type"),
        [
            (Inhibition, True, "INHIBITION"),
            (NegativeInfluence, False, "NEGATIVE_INFLUENCE"),
            (UnknownInhibition, True, "UNKNOWN_INHIBITION"),
            (UnknownNegativeInfluence, False, "UNKNOWN_NEGATIVE_INFLUENCE"),
        ],
    )
    def test_normalized_class_writes_its_own_spelling(
        self,
        map_,
        model_element_cls,
        target_is_a_phenotype,
        expected_reaction_type,
    ):
        modulations = _modulations_by_id(map_)
        source_modulation = (
            modulations["re1"] if target_is_a_phenotype else modulations["re3"]
        )
        modulation = model_element_cls(
            id_=source_modulation.id_,
            source=source_modulation.source,
            target=source_modulation.target,
        )
        assert get_modulation_reaction_type(modulation) == expected_reaction_type
        assert (
            normalize_modulation_class(model_element_cls, modulation.target)
            is model_element_cls
        )
