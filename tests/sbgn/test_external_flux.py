"""Tests for the external-source/sink flags on processes/reactions."""

import os
import tempfile

import pytest

import momapy.io.core
import momapy.sbgn.pd
import momapy.sbgn.pd.layout
import momapy.celldesigner.model

EMPTY_SET_FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "maps",
    "pd",
    "activated_stat1alpha_induction_of_the_irf1_gene.sbgn",
)


class TestSBGNExternalFlux:
    def test_flag_field_defaults_false(self):
        """Fresh process has both flags defaulting to False."""
        species = momapy.sbgn.pd.UnspecifiedEntity(id_="A")
        process = momapy.sbgn.pd.GenericProcess(
            id_="p1",
            reactants=frozenset({momapy.sbgn.pd.Reactant(id_="r1", element=species)}),
            products=frozenset({momapy.sbgn.pd.Product(id_="p2", element=species)}),
        )
        assert process.has_external_source is False
        assert process.has_external_sink is False

    def test_two_processes_with_external_source_not_equal(self):
        """Two distinct ``∅ → X`` processes targeting different species
        remain distinct because the products differ."""
        a = momapy.sbgn.pd.UnspecifiedEntity(label="A")
        b = momapy.sbgn.pd.UnspecifiedEntity(label="B")
        p_a = momapy.sbgn.pd.GenericProcess(
            reactants=frozenset(),
            products=frozenset({momapy.sbgn.pd.Product(element=a)}),
            has_external_source=True,
        )
        p_b = momapy.sbgn.pd.GenericProcess(
            reactants=frozenset(),
            products=frozenset({momapy.sbgn.pd.Product(element=b)}),
            has_external_source=True,
        )
        assert p_a != p_b
        assert hash(p_a) != hash(p_b)

    def test_a_plus_empty_to_b_plus_empty_distinct_from_a_to_b(self):
        """``A + ∅ → B + ∅`` (both flags set) is distinct from ``A → B`` even
        when the reactant/product sets coincide. This is the case the
        flags option preserves over the deletion option."""
        a = momapy.sbgn.pd.UnspecifiedEntity(id_="A")
        b = momapy.sbgn.pd.UnspecifiedEntity(id_="B")
        plain = momapy.sbgn.pd.GenericProcess(
            id_="plain",
            reactants=frozenset({momapy.sbgn.pd.Reactant(id_="r1", element=a)}),
            products=frozenset({momapy.sbgn.pd.Product(id_="p1", element=b)}),
        )
        with_external = momapy.sbgn.pd.GenericProcess(
            id_="plain",
            reactants=frozenset({momapy.sbgn.pd.Reactant(id_="r1", element=a)}),
            products=frozenset({momapy.sbgn.pd.Product(id_="p1", element=b)}),
            has_external_source=True,
            has_external_sink=True,
        )
        assert plain != with_external

    def test_all_four_flag_combinations_distinct(self):
        """The four flag combinations on otherwise-identical processes
        produce four distinct hashable values."""
        a = momapy.sbgn.pd.UnspecifiedEntity(id_="A")
        b = momapy.sbgn.pd.UnspecifiedEntity(id_="B")
        base_kwargs = dict(
            id_="p",
            reactants=frozenset({momapy.sbgn.pd.Reactant(id_="r", element=a)}),
            products=frozenset({momapy.sbgn.pd.Product(id_="prod", element=b)}),
        )
        combos = {momapy.sbgn.pd.GenericProcess(**base_kwargs) for _ in [0]}
        combos.add(
            momapy.sbgn.pd.GenericProcess(**base_kwargs, has_external_source=True)
        )
        combos.add(momapy.sbgn.pd.GenericProcess(**base_kwargs, has_external_sink=True))
        combos.add(
            momapy.sbgn.pd.GenericProcess(
                **base_kwargs,
                has_external_source=True,
                has_external_sink=True,
            )
        )
        assert len(combos) == 4


class TestSBGNEmptySetRoundTrip:
    """Integration tests on a fixture map containing two empty-set glyphs.

    The fixture map has two ``∅ → X`` processes; reading must populate
    ``has_external_source`` on those processes and preserve both
    ``EmptySetLayout`` instances in ``layout.layout_elements``."""

    @pytest.fixture
    def map_(self):
        if not os.path.exists(EMPTY_SET_FIXTURE):
            pytest.skip(f"fixture {EMPTY_SET_FIXTURE} not found")
        return momapy.io.core.read(EMPTY_SET_FIXTURE).obj

    def test_empty_set_layouts_preserved(self, map_):
        empty_set_layouts = [
            le
            for le in map_.layout.layout_elements
            if isinstance(le, momapy.sbgn.pd.EmptySetLayout)
        ]
        assert len(empty_set_layouts) == 2

    def test_external_source_flag_set_on_two_processes(self, map_):
        flagged = [
            p
            for p in map_.model.processes
            if isinstance(p, momapy.sbgn.pd.StoichiometricProcess)
            and p.has_external_source
        ]
        assert len(flagged) == 2

    def test_roundtrip_preserves_flags(self, map_):
        with tempfile.NamedTemporaryFile(suffix=".sbgn", delete=False, mode="w") as tmp:
            tmp_path = tmp.name
        try:
            momapy.io.core.write(map_, tmp_path, writer="sbgnml-0.3")
            map2 = momapy.io.core.read(tmp_path).obj
        finally:
            os.unlink(tmp_path)
        flagged_before = sorted(
            (p.has_external_source, p.has_external_sink)
            for p in map_.model.processes
            if isinstance(p, momapy.sbgn.pd.StoichiometricProcess)
        )
        flagged_after = sorted(
            (p.has_external_source, p.has_external_sink)
            for p in map2.model.processes
            if isinstance(p, momapy.sbgn.pd.StoichiometricProcess)
        )
        assert flagged_before == flagged_after


class TestCellDesignerExternalFlux:
    def test_flag_field_defaults_false(self):
        from momapy.celldesigner.model import StateTransition

        reaction = StateTransition(reversible=False)
        assert reaction.has_external_source is False
        assert reaction.has_external_sink is False

    def test_flagged_reactions_distinct_by_flags(self):
        from momapy.celldesigner.model import StateTransition

        plain = StateTransition(reversible=False)
        with_source = StateTransition(reversible=False, has_external_source=True)
        with_sink = StateTransition(reversible=False, has_external_sink=True)
        with_both = StateTransition(
            reversible=False,
            has_external_source=True,
            has_external_sink=True,
        )
        assert len({plain, with_source, with_sink, with_both}) == 4
