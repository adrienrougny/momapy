"""Tests for SVG rendering."""

import os
import pytest
import momapy.rendering.core

pytestmark = pytest.mark.slow


class TestSVGRendering:
    """Tests for SVG rendering."""

    def test_render_svg_native(self, sample_map, temp_dir):
        """Test rendering with svg-native renderer."""
        output_file = os.path.join(temp_dir, "test_output.svg")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="svg", renderer="svg-native"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_render_svg_native_compat(self, sample_map, temp_dir):
        """Test rendering with svg-native-compat renderer."""
        output_file = os.path.join(temp_dir, "test_output_compat.svg")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="svg", renderer="svg-native-compat"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0


class TestGaussianBlurEdgeMode:
    """feGaussianBlur edgeMode handling.

    Encodes the momapy sentinel convention: NoneValue is SVG "none" (explicit
    value) and Python None is SVG "unset" (attribute omitted).
    """

    def _renderer(self, temp_dir):
        import momapy.rendering.svg_native

        output_file = os.path.join(temp_dir, "blur.svg")
        return momapy.rendering.svg_native.SVGNativeRenderer.from_file(
            output_file, 100, 100
        )

    def test_none_value_edge_mode_emits_none(self, temp_dir):
        """The default edge_mode (NoneValue) emits edgeMode="none"."""
        import momapy.drawing

        renderer = self._renderer(temp_dir)
        effect = momapy.drawing.GaussianBlurEffect(std_deviation=2.0)
        assert effect.edge_mode is momapy.drawing.NoneValue
        element = renderer._make_gaussian_blur_effect_element(effect)
        assert element.attributes["edgeMode"] == "none"

    def test_python_none_edge_mode_omits_attribute(self, temp_dir):
        """A Python None edge_mode (unset) omits the edgeMode attribute."""
        import momapy.drawing

        renderer = self._renderer(temp_dir)
        effect = momapy.drawing.GaussianBlurEffect(std_deviation=2.0, edge_mode=None)
        element = renderer._make_gaussian_blur_effect_element(effect)
        assert "edgeMode" not in element.attributes

    def test_explicit_edge_mode_emits_attribute(self, temp_dir):
        """An explicit EdgeMode maps to its edgeMode string."""
        import momapy.drawing

        renderer = self._renderer(temp_dir)
        effect = momapy.drawing.GaussianBlurEffect(
            std_deviation=2.0, edge_mode=momapy.drawing.EdgeMode.WRAP
        )
        element = renderer._make_gaussian_blur_effect_element(effect)
        assert element.attributes["edgeMode"] == "wrap"
