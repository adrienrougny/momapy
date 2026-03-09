"""Tests for momapy.core.fonts module."""

import momapy.core.fonts
import momapy.drawing


class TestGetFontDirectories:
    def test_returns_only_existing_dirs(self):
        dirs = momapy.core.fonts._get_font_directories()
        import os

        for d in dirs:
            assert os.path.isdir(d)


class TestScanFonts:
    def test_returns_non_empty_list(self):
        entries = momapy.core.fonts._scan_fonts()
        assert len(entries) > 0

    def test_entries_have_valid_fields(self):
        entries = momapy.core.fonts._scan_fonts()
        for entry in entries[:10]:
            assert isinstance(entry.path, str)
            assert isinstance(entry.family, str)
            assert entry.family == entry.family.lower()
            assert isinstance(entry.weight, int)
            assert isinstance(entry.is_italic, bool)


class TestScoreFont:
    def test_exact_match_scores_zero(self):
        entry = momapy.core.fonts._FontEntry(
            path="/fake.ttf",
            family="arial",
            weight=400,
            is_italic=False,
        )
        score = momapy.core.fonts._score_font(
            entry, "arial", 400, False
        )
        assert score == 0.0

    def test_family_mismatch_adds_ten(self):
        entry = momapy.core.fonts._FontEntry(
            path="/fake.ttf",
            family="times",
            weight=400,
            is_italic=False,
        )
        score = momapy.core.fonts._score_font(
            entry, "arial", 400, False
        )
        assert score >= 10.0

    def test_italic_mismatch_adds_one(self):
        entry = momapy.core.fonts._FontEntry(
            path="/fake.ttf",
            family="arial",
            weight=400,
            is_italic=True,
        )
        score = momapy.core.fonts._score_font(
            entry, "arial", 400, False
        )
        assert score == 1.0

    def test_weight_difference(self):
        entry = momapy.core.fonts._FontEntry(
            path="/fake.ttf",
            family="arial",
            weight=700,
            is_italic=False,
        )
        score = momapy.core.fonts._score_font(
            entry, "arial", 400, False
        )
        assert 0 < score < 1


class TestFindFont:
    def test_find_font_returns_path(self):
        path = momapy.core.fonts.find_font(
            family="sans-serif",
            weight=momapy.drawing.FontWeight.NORMAL,
            style=momapy.drawing.FontStyle.NORMAL,
        )
        assert path is not None
        assert isinstance(path, str)

    def test_find_font_bold(self):
        path = momapy.core.fonts.find_font(
            family="sans-serif",
            weight=momapy.drawing.FontWeight.BOLD,
            style=momapy.drawing.FontStyle.NORMAL,
        )
        assert path is not None

    def test_find_font_italic(self):
        path = momapy.core.fonts.find_font(
            family="sans-serif",
            weight=momapy.drawing.FontWeight.NORMAL,
            style=momapy.drawing.FontStyle.ITALIC,
        )
        assert path is not None

    def test_find_font_weight_int(self):
        path = momapy.core.fonts.find_font(
            family="sans-serif",
            weight=700,
            style=momapy.drawing.FontStyle.NORMAL,
        )
        assert path is not None

    def test_find_font_weight_enum(self):
        path = momapy.core.fonts.find_font(
            family="sans-serif",
            weight=momapy.drawing.FontWeight.BOLD,
            style=momapy.drawing.FontStyle.NORMAL,
        )
        assert path is not None

    def test_find_font_unknown_family(self):
        path = momapy.core.fonts.find_font(
            family="nonexistent_font_family_xyz",
            weight=momapy.drawing.FontWeight.NORMAL,
            style=momapy.drawing.FontStyle.NORMAL,
        )
        # Should return a fallback font, not None
        assert path is not None
