"""Tests for Skia rendering."""

import pytest
import os

pytestmark = pytest.mark.slow


# Check if Skia is available
try:
    import skia  # noqa: F401

    SKIA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SKIA_AVAILABLE = False


@pytest.mark.skipif(
    not SKIA_AVAILABLE,
    reason="skia-python not installed (install with: pip install momapy[skia])",
)
class TestSkiaRendering:
    """Tests for Skia rendering."""

    def test_render_skia_png(self, sample_map, temp_dir):
        """Test rendering with skia renderer to PNG format."""
        import momapy.rendering.skia

        output_file = os.path.join(temp_dir, "test_output.png")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="png", renderer="skia"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_render_skia_pdf(self, sample_map, temp_dir):
        """Test rendering with skia renderer to PDF format."""
        import momapy.rendering.skia

        output_file = os.path.join(temp_dir, "test_output.pdf")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="pdf", renderer="skia"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_default_edge_mode_resolves_to_tile_mode(self):
        """The default blur edge_mode (NoneValue) resolves to a TileMode.

        Regression (finding 5): the mapping was keyed on None, but
        GaussianBlurEffect.edge_mode defaults to NoneValue, so the lookup
        raised KeyError for any directly-built blur with the default edge mode.
        """
        import momapy.drawing
        import momapy.rendering.skia

        mapping = momapy.rendering.skia.SkiaRenderer._fe_gaussian_blur_edgemode_tilemode_mapping
        assert momapy.drawing.NoneValue in mapping
        assert None not in mapping
        effect = momapy.drawing.GaussianBlurEffect(std_deviation=2.0)
        assert mapping[effect.edge_mode] is skia.TileMode.kDecal
