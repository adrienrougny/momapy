"""Tests for Skia rendering."""

import pytest
import os
import momapy.rendering.core


# Check if Skia is available
try:
    import skia

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
