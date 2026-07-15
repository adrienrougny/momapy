"""Tests for the momapy.sbgn subpackage."""


class TestSBGNCoreModule:
    """Tests for SBGN subpackage imports and basic functionality."""

    def test_sbgn_import(self):
        """Test that the sbgn package can be imported."""
        import momapy.sbgn

        assert momapy.sbgn is not None

    def test_sbgn_pd_import(self):
        """Test that sbgn.pd module can be imported."""
        import momapy.sbgn.pd

        assert momapy.sbgn.pd is not None

    def test_sbgn_af_import(self):
        """Test that sbgn.af module can be imported."""
        import momapy.sbgn.af

        assert momapy.sbgn.af is not None

    def test_sbgn_utils_import(self):
        """Test that sbgn.utils module can be imported."""
        import momapy.sbgn.utils

        assert momapy.sbgn.utils is not None


class TestSBGNModelElements:
    """Tests for SBGN model element classes."""

    def test_process_creation(self):
        """Test creating a Process model element."""
        import momapy.sbgn.pd

        process = momapy.sbgn.pd.Process()
        assert process is not None

    def test_generic_process_creation(self):
        """Test creating a GenericProcess model element."""
        import momapy.sbgn.pd

        process = momapy.sbgn.pd.GenericProcess()
        assert process is not None
        assert hasattr(process, "reactants")
        assert hasattr(process, "products")
        assert hasattr(process, "reversible")

    def test_macromolecule_creation(self):
        """Test creating a Macromolecule model element."""
        import momapy.sbgn.pd

        entity = momapy.sbgn.pd.Macromolecule()
        assert entity is not None


class TestSBGNMap:
    """Tests for SBGN Map class."""

    def test_pd_map_creation(self):
        """Test creating a Process Description Map."""
        import momapy.sbgn.pd

        map_ = momapy.sbgn.pd.SBGNPDMap()
        assert map_ is not None

    def test_af_map_creation(self):
        """Test creating an Activity Flow Map."""
        import momapy.sbgn.af

        map_ = momapy.sbgn.af.SBGNAFMap()
        assert map_ is not None


def _collect_stroke_widths(drawing_elements):
    """Recursively collect all non-None stroke widths from drawing elements."""
    stroke_widths = set()
    for drawing_element in drawing_elements:
        stroke_width = getattr(drawing_element, "stroke_width", None)
        if stroke_width is not None:
            stroke_widths.add(stroke_width)
        stroke_widths |= _collect_stroke_widths(
            getattr(drawing_element, "elements", [])
        )
    return stroke_widths


class TestSBGNAFBorderStrokeWidth:
    """AF compartment/submap thick borders actually reach the drawing."""

    def test_compartment_uses_stroke_width(self):
        """CompartmentLayout renders its border with the intended thick width."""
        import momapy.geometry
        import momapy.sbgn.af

        layout_element = momapy.sbgn.af.CompartmentLayout(
            position=momapy.geometry.Point(0.0, 0.0)
        )
        assert layout_element.stroke_width == 3.25
        assert not hasattr(layout_element, "border_stroke_width")
        assert 3.25 in _collect_stroke_widths(layout_element.drawing_elements())

    def test_submap_uses_stroke_width(self):
        """SubmapLayout renders its border with the intended thick width."""
        import momapy.geometry
        import momapy.sbgn.af

        layout_element = momapy.sbgn.af.SubmapLayout(
            position=momapy.geometry.Point(0.0, 0.0)
        )
        assert layout_element.stroke_width == 2.25
        assert not hasattr(layout_element, "border_stroke_width")
        assert 2.25 in _collect_stroke_widths(layout_element.drawing_elements())


class TestSBGNKeywordOnly:
    """The SBGN layout bases must not leak positional style parameters."""

    def test_sbgn_layout_bases_are_keyword_only(self):
        """SBGNNode/arc bases and _MultiMixin expose no positional-or-keyword fields.

        Regression (finding 29): these were `@dataclass(frozen=True)` without
        `kw_only=True`, so style fields (fill/stroke/...) leaked as positional
        parameters onto every concrete subclass.
        """
        import inspect

        import momapy.sbgn.elements

        bases = [
            momapy.sbgn.elements.SBGNNode,
            momapy.sbgn.elements.SBGNSingleHeadedArc,
            momapy.sbgn.elements.SBGNDoubleHeadedArc,
            momapy.sbgn.elements._MultiMixin,
        ]
        for base in bases:
            for name, parameter in inspect.signature(base).parameters.items():
                assert parameter.kind not in (
                    parameter.POSITIONAL_ONLY,
                    parameter.POSITIONAL_OR_KEYWORD,
                ), f"{base.__name__}.{name} is positional"


class TestSBGNUtils:
    """Tests for SBGN utility functions."""

    def test_utils_module_exists(self):
        """Test that SBGN utils module exists and has expected functions."""
        import momapy.sbgn.utils

        # Check that the module exists
        assert momapy.sbgn.utils is not None
