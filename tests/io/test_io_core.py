"""Tests for momapy.io.core module."""
import pytest
import momapy.io.core


def test_readers_dict_exists():
    """Test that readers dictionary exists."""
    assert isinstance(momapy.io.core.readers, dict)


def test_writers_dict_exists():
    """Test that writers dictionary exists."""
    assert isinstance(momapy.io.core.writers, dict)


def test_register_reader():
    """Test register_reader function."""
    class DummyReader:
        pass

    momapy.io.core.register_reader("test_reader", DummyReader)
    assert "test_reader" in momapy.io.core.readers
    assert momapy.io.core.readers["test_reader"] == DummyReader


def test_register_writer():
    """Test register_writer function."""
    class DummyWriter:
        pass

    momapy.io.core.register_writer("test_writer", DummyWriter)
    assert "test_writer" in momapy.io.core.writers
    assert momapy.io.core.writers["test_writer"] == DummyWriter


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
    assert hasattr(momapy.io.core, 'read')
    assert callable(momapy.io.core.read)


def test_write_function_exists():
    """Test that write function exists."""
    assert hasattr(momapy.io.core, 'write')
    assert callable(momapy.io.core.write)
