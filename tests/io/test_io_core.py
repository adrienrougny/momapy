"""Tests for momapy.io.core module."""

import pytest
import momapy.io
import momapy.io.core


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
    assert result.exceptions == []


def test_reader_result_creation():
    """Test ReaderResult creation."""
    result = momapy.io.core.ReaderResult()
    assert result.exceptions == []
    assert result.obj is None


def test_writer_result_creation():
    """Test WriterResult creation."""
    result = momapy.io.core.WriterResult()
    assert result.exceptions == []
    assert result.obj is None


def test_read_function_exists():
    """Test that read function exists."""
    assert hasattr(momapy.io.core, "read")
    assert callable(momapy.io.core.read)


def test_write_function_exists():
    """Test that write function exists."""
    assert hasattr(momapy.io.core, "write")
    assert callable(momapy.io.core.write)
