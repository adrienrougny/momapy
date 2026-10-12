"""Tests for momapy.io.core module."""

import glob
import os

import pytest

import momapy.io
import momapy.io.core

_MAPS_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
_CELLDESIGNER_FILE = os.path.join(
    _MAPS_DIR, "celldesigner", "maps", "external_flux.xml"
)
_PLAIN_SBML_FILE = os.path.join(_MAPS_DIR, "sbml", "models", "BIOMD0000000595_url.xml")
# UTF-8 file with bytes that are undecodable in cp1252 (curly quotes).
_UTF8_ONLY_SBML_FILE = os.path.join(
    _MAPS_DIR, "sbml", "models", "Zake2021_Metformin_Human_multiple_PO_dose.xml"
)


def _detect_reader_name(file_path):
    """Replicate ``read()``'s auto-detection without parsing the file."""
    names = momapy.io.reader_registry.list_available_in_registration_order()
    for name in names:
        if momapy.io.core.get_reader(name).check_file(file_path):
            return name
    return None


def test_reader_registry_exists():
    """Test that reader registry exists."""
    assert hasattr(momapy.io, "reader_registry")


def test_writer_registry_exists():
    """Test that writer registry exists."""
    assert hasattr(momapy.io, "writer_registry")


def test_register_reader():
    """Test register_reader function."""

    class DummyReader(momapy.io.core.Reader):
        @classmethod
        def read(cls, file_path, **options):
            return momapy.io.core.ReaderResult()

        @classmethod
        def check_file(cls, file_path):
            return False

    try:
        momapy.io.register_reader("test_reader", DummyReader)
        assert momapy.io.reader_registry.is_available("test_reader")
        assert momapy.io.reader_registry.get("test_reader") == DummyReader
    finally:
        # Restore original state - remove test reader
        if "test_reader" in momapy.io.reader_registry.list_loaded():
            del momapy.io.reader_registry._loaded_plugins["test_reader"]


def test_register_writer():
    """Test register_writer function."""

    class DummyWriter(momapy.io.core.Writer):
        @classmethod
        def write(cls, obj, file_path, **options):
            return momapy.io.core.WriterResult()

    try:
        momapy.io.register_writer("test_writer", DummyWriter)
        assert momapy.io.writer_registry.is_available("test_writer")
        assert momapy.io.writer_registry.get("test_writer") == DummyWriter
    finally:
        # Restore original state - remove test writer
        if "test_writer" in momapy.io.writer_registry.list_loaded():
            del momapy.io.writer_registry._loaded_plugins["test_writer"]


def test_io_result_creation():
    """Test IOResult creation."""
    result = momapy.io.core.IOResult()
    assert result is not None


def test_reader_result_creation():
    """Test ReaderResult creation."""
    result = momapy.io.core.ReaderResult()
    assert result.obj is None


def test_writer_result_creation():
    """Test WriterResult creation."""
    result = momapy.io.core.WriterResult()
    assert result.obj is None


def test_read_function_exists():
    """Test that read function exists."""
    assert hasattr(momapy.io.core, "read")
    assert callable(momapy.io.core.read)


def test_write_function_exists():
    """Test that write function exists."""
    assert hasattr(momapy.io.core, "write")
    assert callable(momapy.io.core.write)


def test_reader_registration_order_celldesigner_before_sbml():
    """CellDesigner must be registered (hence checked) before SBML."""
    order = momapy.io.reader_registry.list_available_in_registration_order()
    assert "celldesigner" in order
    assert "sbml" in order
    assert order.index("celldesigner") < order.index("sbml")


def test_check_file_is_independent_of_locale_encoding(monkeypatch):
    """check_file must not depend on the platform's locale encoding.

    A UTF-8 map file whose bytes are undecodable in the locale codepage (cp1252
    on Windows) used to raise UnicodeDecodeError inside check_file, which was
    swallowed and reported as "no suitable registered reader".
    """
    real_open = open

    def cp1252_open(file, mode="r", *args, **kwargs):
        if "b" not in mode and "encoding" not in kwargs:
            kwargs["encoding"] = "cp1252"
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", cp1252_open)
    reader = momapy.io.core.get_reader("sbml")
    assert reader.check_file(_UTF8_ONLY_SBML_FILE) is True


def test_sbml_check_file_accepts_celldesigner():
    """A CellDesigner file is also SBML, so both readers accept it."""
    sbml_reader = momapy.io.core.get_reader("sbml")
    celldesigner_reader = momapy.io.core.get_reader("celldesigner")
    assert celldesigner_reader.check_file(_CELLDESIGNER_FILE) is True
    assert sbml_reader.check_file(_CELLDESIGNER_FILE) is True


_SBML_FILE_CONTENTS = {
    "newline_after_tag": (
        "<sbml\n"
        '  xmlns="http://www.sbml.org/sbml/level2/version4" level="2" version="4">\n'
        '  <model id="m"/>\n'
        "</sbml>\n"
    ),
    "prefixed_root": (
        '<s:sbml xmlns:s="http://www.sbml.org/sbml/level2/version4"'
        ' level="2" version="4">\n'
        '  <s:model id="m"/>\n'
        "</s:sbml>\n"
    ),
}


@pytest.mark.parametrize("content_name", sorted(_SBML_FILE_CONTENTS))
def test_sbml_check_file_accepts_valid_root_tags(tmp_path, content_name):
    """A root tag followed by a newline or carrying a prefix is SBML."""
    file_path = tmp_path / "model.xml"
    file_path.write_text(_SBML_FILE_CONTENTS[content_name])
    assert momapy.io.core.get_reader("sbml").check_file(file_path) is True
    result = momapy.io.read(file_path)
    assert result.obj.model is not None


def test_sbml_check_file_rejects_other_root_tag(tmp_path):
    """A root tag that only starts with "sbml" is not SBML."""
    file_path = tmp_path / "model.xml"
    file_path.write_text(
        '<sbmlfoo xmlns="http://www.sbml.org/sbml/level2/version4"></sbmlfoo>\n'
    )
    assert momapy.io.core.get_reader("sbml").check_file(file_path) is False


def test_read_autodetects_celldesigner_for_cd_file():
    """Auto-detection picks CellDesigner for a CD file (registration order)."""
    assert _detect_reader_name(_CELLDESIGNER_FILE) == "celldesigner"


def test_read_autodetects_sbml_for_plain_sbml_file():
    """Auto-detection picks SBML for a plain (non-CD) SBML file."""
    assert _detect_reader_name(_PLAIN_SBML_FILE) == "sbml"


_XML_READER_NAMES = ["sbgnml-0.2", "sbgnml-0.3", "celldesigner", "sbml"]
_EXPECTED_READER_FILES = (
    [
        (path, "sbgnml")
        for path in glob.glob(
            os.path.join(_MAPS_DIR, "sbgn", "**", "*.sbgn"), recursive=True
        )
    ]
    + [
        (path, "celldesigner")
        for path in glob.glob(
            os.path.join(_MAPS_DIR, "celldesigner", "**", "*.xml"), recursive=True
        )
    ]
    + [
        (path, "sbml")
        for path in glob.glob(
            os.path.join(_MAPS_DIR, "sbml", "**", "*.xml"), recursive=True
        )
    ]
)


@pytest.mark.parametrize("file_path, reader_name", _EXPECTED_READER_FILES)
def test_read_autodetects_reader_from_root_element(file_path, reader_name):
    """Every test map is detected with the reader of its format."""
    assert _detect_reader_name(file_path) == reader_name


def test_xml_check_file_rejects_binary_file_with_namespaces(tmp_path):
    """A non-XML file mentioning every format namespace is rejected."""
    file_path = tmp_path / "binary.bin"
    file_path.write_bytes(
        b"\x80\x04<sbml http://www.sbml.org/2001/ns/celldesigner\n"
        b"http://sbgn.org/libsbgn/0.2 http://sbgn.org/libsbgn/0.3\n"
    )
    for name in _XML_READER_NAMES:
        assert momapy.io.core.get_reader(name).check_file(file_path) is False


def test_read_rejects_pickled_celldesigner_result_with_notes(tmp_path):
    """A pickled CellDesigner result with notes is not taken for CellDesigner."""
    result = momapy.io.read(_CELLDESIGNER_FILE)
    file_path = tmp_path / "map.pkl"
    momapy.io.write(
        result.obj,
        file_path,
        writer="pickle",
        element_to_notes={
            result.obj.model: [
                '<html xmlns:celldesigner="http://www.sbml.org/2001/ns/celldesigner"/>'
            ]
        },
    )
    with pytest.raises(ValueError, match="suitable registered reader"):
        momapy.io.read(file_path)


def test_sbml_with_namespaces_in_notes_is_detected_as_sbml(tmp_path):
    """Namespaces mentioned below the root do not change the detected format."""
    file_path = tmp_path / "model.xml"
    file_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sbml xmlns="http://www.sbml.org/sbml/level2/version4" level="2" version="4">\n'
        '  <model id="m">\n'
        "    <notes>\n"
        '      <p xmlns="http://www.w3.org/1999/xhtml"'
        ' xmlns:celldesigner="http://www.sbml.org/2001/ns/celldesigner">'
        "http://sbgn.org/libsbgn/0.3</p>\n"
        "    </notes>\n"
        "  </model>\n"
        "</sbml>\n"
    )
    assert _detect_reader_name(file_path) == "sbml"
