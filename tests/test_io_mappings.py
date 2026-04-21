"""Regression tests for ReaderResult ID mappings.

Guards against a regression where ``source_id_to_model_element`` would be
empty for formats whose ``Model`` class is not a ``ModelElement``, and
where the ``Model`` itself could leak into the result dict.
"""

import os
import pytest

import momapy.core.elements
import momapy.core.model
import momapy.io.core
from momapy.celldesigner.model import CellDesignerModel


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SBGN_FIXTURE = os.path.join(TESTS_DIR, "sbgn", "maps", "pd", "mapk_cascade.sbgn")
CELLDESIGNER_FIXTURE = os.path.join(
    TESTS_DIR, "celldesigner", "maps", "Apoptosis_pathway.xml"
)


class TestSourceIdToModelElement:
    """source_id_to_model_element must be populated and must not contain Model."""

    @pytest.mark.parametrize(
        "fixture_path",
        [
            pytest.param(SBGN_FIXTURE, id="sbgn-pd"),
            pytest.param(CELLDESIGNER_FIXTURE, id="celldesigner"),
        ],
    )
    def test_non_empty(self, fixture_path):
        if not os.path.exists(fixture_path):
            pytest.skip(f"fixture not found: {fixture_path}")
        result = momapy.io.core.read(fixture_path)
        assert result.source_id_to_model_element is not None
        assert len(result.source_id_to_model_element) > 0

    @pytest.mark.parametrize(
        "fixture_path",
        [
            pytest.param(SBGN_FIXTURE, id="sbgn-pd"),
            pytest.param(CELLDESIGNER_FIXTURE, id="celldesigner"),
        ],
    )
    def test_does_not_contain_model_itself(self, fixture_path):
        if not os.path.exists(fixture_path):
            pytest.skip(f"fixture not found: {fixture_path}")
        result = momapy.io.core.read(fixture_path)
        model = result.obj.model
        for value in result.source_id_to_model_element.values():
            assert not isinstance(value, momapy.core.model.Model)
        assert model.id_ not in result.source_id_to_model_element

    @pytest.mark.parametrize(
        "fixture_path",
        [
            pytest.param(SBGN_FIXTURE, id="sbgn-pd"),
            pytest.param(CELLDESIGNER_FIXTURE, id="celldesigner"),
        ],
    )
    def test_values_are_model_elements(self, fixture_path):
        if not os.path.exists(fixture_path):
            pytest.skip(f"fixture not found: {fixture_path}")
        result = momapy.io.core.read(fixture_path)
        for value in result.source_id_to_model_element.values():
            assert isinstance(value, momapy.core.elements.ModelElement)


class TestModelNotAModelElement:
    """A momapy ``Model`` must never be a ``ModelElement``."""

    def test_sbgn_pd_model(self):
        import momapy.sbgn.pd

        assert not issubclass(
            momapy.sbgn.pd.SBGNPDModel, momapy.core.elements.ModelElement
        )

    def test_sbgn_af_model(self):
        import momapy.sbgn.af

        assert not issubclass(
            momapy.sbgn.af.SBGNAFModel, momapy.core.elements.ModelElement
        )

    def test_sbml_model(self):
        import momapy.sbml.model

        assert not issubclass(
            momapy.sbml.model.SBMLModel, momapy.core.elements.ModelElement
        )

    def test_celldesigner_model(self):
        import momapy.celldesigner.model

        assert not issubclass(
            CellDesignerModel,
            momapy.core.elements.ModelElement,
        )
