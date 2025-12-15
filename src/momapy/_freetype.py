import freetype

_SCALE = 64.0


def make_face_from_font_file_path(font_file_path, font_size):
    face = freetype.Face(font_file_path)
    face.set_char_size(font_size * int(_SCALE))
    return face


def get_string_logical_bbox(text, face):
    ascent, descent, _ = get_face_parameters(face)
    total_advance = 0
    previous_glyph_index = None
    for char in text:
        current_glyph_index = face.get_char_index(char)
        face.load_glyph(current_glyph_index, freetype.FT_LOAD_DEFAULT)
        if previous_glyph_index is not None:
            kerning = face.get_kerning(previous_glyph_index, current_glyph_index)
            total_advance += kerning.x / _SCALE
        total_advance += face.glyph.metrics.horiAdvance / _SCALE
        previous_glyph_index = current_glyph_index
    return (0, 0, total_advance, ascent + descent)


def get_face_parameters(face):
    ascent = face.size.ascender / _SCALE  # from baseline to top
    descent = abs(face.size.descender / _SCALE)  # from baseline to bottom
    height = face.size.height / _SCALE  # between baselines
    return ascent, descent, height
