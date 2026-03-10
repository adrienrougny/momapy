"""Font file lookup using uharfbuzz for metadata reading."""

import os
import platform
import typing

import uharfbuzz

import momapy.drawing


class _FontEntry(typing.NamedTuple):
    """A cached font entry with metadata."""

    path: str
    family: str
    weight: int
    is_italic: bool


_FONT_WEIGHT_MAP: dict[momapy.drawing.FontWeight, int] = {
    momapy.drawing.FontWeight.NORMAL: 400,
    momapy.drawing.FontWeight.BOLD: 700,
    momapy.drawing.FontWeight.BOLDER: 800,
    momapy.drawing.FontWeight.LIGHTER: 300,
}

_FONT_EXTENSIONS = frozenset({".ttf", ".otf", ".ttc"})

_font_cache: list[_FontEntry] | None = None
_query_cache: dict[
    tuple[str, momapy.drawing.FontWeight | int, momapy.drawing.FontStyle],
    str | None,
] = {}


def _get_font_directories() -> list[str]:
    """Return existing system font directories for the current platform.

    Returns:
        List of existing font directory paths.
    """
    system = platform.system()
    home = os.path.expanduser("~")
    if system == "Linux":
        candidates = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.join(home, ".local", "share", "fonts"),
            os.path.join(home, ".fonts"),
        ]
    elif system == "Darwin":
        candidates = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.join(home, "Library", "Fonts"),
        ]
    elif system == "Windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        candidates = [
            os.path.join(windir, "Fonts"),
            os.path.join(home, "AppData", "Local", "Microsoft", "Windows", "Fonts"),
        ]
    else:
        candidates = []
    return [candidate for candidate in candidates if os.path.isdir(candidate)]


def _read_font_metadata(path: str) -> list[_FontEntry]:
    """Read font metadata from a font file using uharfbuzz.

    Args:
        path: Path to the font file.

    Returns:
        List of font entries (multiple for .ttc files).
    """
    entries: list[_FontEntry] = []
    try:
        blob = uharfbuzz.Blob.from_file_path(path)
        face = uharfbuzz.Face(blob)
        num_faces = face.count
    except Exception:
        return entries
    for index in range(num_faces):
        try:
            face = uharfbuzz.Face(blob, index)
            family = face.get_name(1)
            if family is None:
                continue
            family = family.lower()
            subfamily = face.get_name(2)
            subfamily = subfamily.lower() if subfamily else ""
            # Read OS/2 table for weight and italic
            os2_data = face.table_tags
            weight = 400
            is_italic = False
            if b"OS/2" in os2_data:
                os2_blob = face.reference_table(b"OS/2")
                os2_bytes = memoryview(os2_blob)
                if len(os2_bytes) >= 6:
                    weight = int.from_bytes(os2_bytes[4:6], byteorder="big")
                if len(os2_bytes) >= 64:
                    fs_selection = int.from_bytes(os2_bytes[62:64], byteorder="big")
                    is_italic = bool(fs_selection & 1)
            # Fallback: check subfamily string
            if not is_italic and ("italic" in subfamily or "oblique" in subfamily):
                is_italic = True
            entries.append(
                _FontEntry(
                    path=path,
                    family=family,
                    weight=weight,
                    is_italic=is_italic,
                )
            )
        except Exception:
            continue
    return entries


def _scan_fonts() -> list[_FontEntry]:
    """Scan system font directories and return all font entries.

    Returns:
        List of all discovered font entries.
    """
    entries: list[_FontEntry] = []
    for font_dir in _get_font_directories():
        for dirpath, _, filenames in os.walk(font_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in _FONT_EXTENSIONS:
                    path = os.path.join(dirpath, filename)
                    entries.extend(_read_font_metadata(path))
    return entries


def _get_or_make_font_cache() -> list[_FontEntry]:
    """Return the font cache, populating it on first call.

    Returns:
        List of cached font entries.
    """
    global _font_cache, _query_cache
    if _font_cache is None:
        _font_cache = _scan_fonts()
        _query_cache = {}
    return _font_cache


def _score_font(
    entry: _FontEntry,
    family: str,
    weight: int,
    want_italic: bool,
) -> float:
    """Score a font entry against desired properties.

    Lower is better.

    Args:
        entry: The font entry to score.
        family: Desired font family (lowercased).
        weight: Desired font weight (100-900).
        want_italic: Whether italic is desired.

    Returns:
        A score where lower is better.
    """
    family_score = 0.0 if entry.family == family else 1.0
    style_score = 0.0 if entry.is_italic == want_italic else 1.0
    weight_score = abs(entry.weight - weight) / 900
    return family_score * 10 + style_score + weight_score


def find_font(
    family: str,
    weight: momapy.drawing.FontWeight | int,
    style: momapy.drawing.FontStyle,
) -> str | None:
    """Find the best matching font file path.

    Args:
        family: Font family name.
        weight: Font weight as FontWeight enum or int (100-900).
        style: Font style.

    Returns:
        Path to the best matching font file, or None if no fonts found.
    """
    cache_key = (family, weight, style)
    cached = _query_cache.get(cache_key)
    if cached is not None or cache_key in _query_cache:
        return cached
    font_cache = _get_or_make_font_cache()
    if not font_cache:
        _query_cache[cache_key] = None
        return None
    if isinstance(weight, momapy.drawing.FontWeight):
        weight = _FONT_WEIGHT_MAP[weight]
    want_italic = style in (
        momapy.drawing.FontStyle.ITALIC,
        momapy.drawing.FontStyle.OBLIQUE,
    )
    family_lower = family.lower()
    best_font_entry = min(
        font_cache,
        key=lambda font_entry: _score_font(
            font_entry, family_lower, weight, want_italic
        ),
    )
    result = best_font_entry.path
    _query_cache[cache_key] = result
    return result
