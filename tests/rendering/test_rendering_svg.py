"""Tests for SVG rendering."""
import os
import momapy.rendering.core


class TestSVGRendering:
    """Tests for SVG rendering."""

    def test_render_svg_native(self, sample_map, temp_dir):
        """Test rendering with svg-native renderer."""
        output_file = os.path.join(temp_dir, "test_output.svg")
        momapy.rendering.core.render_layout_element(
            sample_map.layout,
            output_file,
            format_="svg",
            renderer="svg-native"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_render_svg_native_compat(self, sample_map, temp_dir):
        """Test rendering with svg-native-compat renderer."""
        output_file = os.path.join(temp_dir, "test_output_compat.svg")
        momapy.rendering.core.render_layout_element(
            sample_map.layout,
            output_file,
            format_="svg",
            renderer="svg-native-compat"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0
