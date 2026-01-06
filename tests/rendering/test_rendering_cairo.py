"""Tests for Cairo rendering."""

import pytest
import os
import momapy.rendering.core


# Check if Cairo is available
try:
    # Try to import the momapy cairo renderer module itself
    # This will fail if any of the dependencies are missing
    import momapy.rendering.cairo

    CAIRO_AVAILABLE = True
except (ImportError, ValueError, AttributeError, ModuleNotFoundError, Exception):
    CAIRO_AVAILABLE = False


@pytest.mark.skipif(
    not CAIRO_AVAILABLE,
    reason="Cairo dependencies not installed (install with: pip install momapy[cairo])",
)
class TestCairoRendering:
    """Tests for Cairo rendering."""

    def test_render_cairo_png(self, sample_map, temp_dir):
        """Test rendering with cairo renderer to PNG format."""
        import momapy.rendering.cairo

        output_file = os.path.join(temp_dir, "test_output_cairo.png")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="png", renderer="cairo"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_render_cairo_pdf(self, sample_map, temp_dir):
        """Test rendering with cairo renderer to PDF format."""
        import momapy.rendering.cairo

        output_file = os.path.join(temp_dir, "test_output_cairo.pdf")
        momapy.rendering.core.render_layout_element(
            sample_map.layout, output_file, format_="pdf", renderer="cairo"
        )
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0
