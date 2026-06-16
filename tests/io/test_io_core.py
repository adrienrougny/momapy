"""Tests for momapy.io.core module."""

import os

import momapy.io
import momapy.io.core

_MAPS_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
_CELLDESIGNER_FILE = os.path.join(
    _MAPS_DIR, "celldesigner", "maps", "external_flux.xml"
)
_PLAIN_SBML_FILE = os.path.join(_MAPS_DIR, "sbml", "models", "BIOMD0000000595_url.xml")


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

    # Save original state
    original_readers = momapy.io.reader_registry.list_loaded()

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

    # Save original state
    original_writers = momapy.io.writer_registry.list_loaded()

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


def test_sbml_check_file_accepts_celldesigner():
    """A CellDesigner file is also SBML, so both readers accept it."""
    sbml_reader = momapy.io.core.get_reader("sbml")
    celldesigner_reader = momapy.io.core.get_reader("celldesigner")
    assert celldesigner_reader.check_file(_CELLDESIGNER_FILE) is True
    assert sbml_reader.check_file(_CELLDESIGNER_FILE) is True


def test_read_autodetects_celldesigner_for_cd_file():
    """Auto-detection picks CellDesigner for a CD file (registration order)."""
    assert _detect_reader_name(_CELLDESIGNER_FILE) == "celldesigner"


def test_read_autodetects_sbml_for_plain_sbml_file():
    """Auto-detection picks SBML for a plain (non-CD) SBML file."""
    assert _detect_reader_name(_PLAIN_SBML_FILE) == "sbml"
