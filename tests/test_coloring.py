"""Tests for momapy.coloring module."""
import pytest
import momapy.coloring


class TestColor:
    """Tests for Color class."""

    def test_color_creation_rgb(self):
        """Test creating a Color from RGB."""
        color = momapy.coloring.Color(255, 128, 64)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == 1.0

    def test_color_creation_rgba(self):
        """Test creating a Color from RGBA."""
        color = momapy.coloring.Color(255, 128, 64, 0.5)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == 0.5

    def test_color_or_operator(self):
        """Test Color alpha setting with | operator."""
        color = momapy.coloring.Color(255, 0, 0)
        color_with_alpha = color | 50
        assert color_with_alpha.alpha == 0.5

    def test_color_or_operator_invalid(self):
        """Test Color | operator with invalid alpha."""
        color = momapy.coloring.Color(255, 0, 0)
        with pytest.raises(ValueError):
            color | 150  # alpha > 100

    def test_color_to_rgba(self):
        """Test Color to_rgba method."""
        color = momapy.coloring.Color(255, 128, 64, 0.5)
        rgba = color.to_rgba()
        assert rgba == (255, 128, 64, 0.5)

    def test_color_to_rgba_custom_range(self):
        """Test Color to_rgba with custom range."""
        color = momapy.coloring.Color(255, 128, 64, 0.5)
        rgba = color.to_rgba(rgb_range=(0.0, 1.0))
        assert rgba[0] == pytest.approx(1.0, rel=0.01)
        assert rgba[1] == pytest.approx(0.502, rel=0.01)
        assert rgba[2] == pytest.approx(0.251, rel=0.01)

    def test_color_to_rgb(self):
        """Test Color to_rgb method."""
        color = momapy.coloring.Color(255, 128, 64)
        rgb = color.to_rgb()
        assert rgb == (255, 128, 64)

    def test_color_to_hex(self):
        """Test Color to_hex method."""
        color = momapy.coloring.Color(255, 128, 64)
        hex_str = color.to_hex()
        assert hex_str == "#ff8040"

    def test_color_to_hexa(self):
        """Test Color to_hexa method."""
        color = momapy.coloring.Color(255, 128, 64, 0.5)
        hexa_str = color.to_hexa()
        # 0.5 * 255 = 127.5, which rounds to 127 (0x7f) with int()
        assert hexa_str == "#ff80407f"

    def test_color_with_alpha(self):
        """Test Color with_alpha method."""
        color = momapy.coloring.Color(255, 128, 64)
        color_with_alpha = color.with_alpha(0.5)
        assert color_with_alpha.red == 255
        assert color_with_alpha.green == 128
        assert color_with_alpha.blue == 64
        assert color_with_alpha.alpha == 0.5

    def test_color_from_rgba(self):
        """Test Color.from_rgba class method."""
        color = momapy.coloring.Color.from_rgba(255, 128, 64, 0.5)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == 0.5

    def test_color_from_rgb(self):
        """Test Color.from_rgb class method."""
        color = momapy.coloring.Color.from_rgb(255, 128, 64)
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == 1.0

    def test_color_from_hex(self):
        """Test Color.from_hex class method."""
        color = momapy.coloring.Color.from_hex("#ff8040")
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64

        # Test without # prefix
        color2 = momapy.coloring.Color.from_hex("ff8040")
        assert color2.red == 255
        assert color2.green == 128
        assert color2.blue == 64

    def test_color_from_hex_invalid(self):
        """Test Color.from_hex with invalid hex string."""
        with pytest.raises(ValueError):
            momapy.coloring.Color.from_hex("#fff")  # too short

    def test_color_from_hexa(self):
        """Test Color.from_hexa class method."""
        color = momapy.coloring.Color.from_hexa("#ff804080")
        assert color.red == 255
        assert color.green == 128
        assert color.blue == 64
        assert color.alpha == pytest.approx(0.5, rel=0.01)

    def test_color_from_hexa_invalid(self):
        """Test Color.from_hexa with invalid hex string."""
        with pytest.raises(ValueError):
            momapy.coloring.Color.from_hexa("#ff8040")  # too short


def test_list_colors():
    """Test list_colors function."""
    colors = momapy.coloring.list_colors()
    assert isinstance(colors, list)
    assert len(colors) > 0
    # Check that black color exists
    color_names = [name for name, _ in colors]
    assert "black" in color_names


def test_has_color():
    """Test has_color function."""
    assert momapy.coloring.has_color("black")
    assert momapy.coloring.has_color("white")
    assert not momapy.coloring.has_color("nonexistent_color_xyz")


def test_predefined_colors():
    """Test that some predefined colors exist."""
    # Test a few standard colors
    assert hasattr(momapy.coloring, 'black')
    assert isinstance(momapy.coloring.black, momapy.coloring.Color)

    assert hasattr(momapy.coloring, 'white')
    assert isinstance(momapy.coloring.white, momapy.coloring.Color)

    # Check black is actually black
    assert momapy.coloring.black.red == 0
    assert momapy.coloring.black.green == 0
    assert momapy.coloring.black.blue == 0
