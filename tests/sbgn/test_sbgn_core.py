"""Tests for momapy.sbgn.core module."""
import pytest


def test_sbgn_core_import():
    """Test that sbgn.core module can be imported."""
    import momapy.sbgn.core
    assert momapy.sbgn.core is not None


def test_sbgn_pd_import():
    """Test that sbgn.pd module can be imported."""
    import momapy.sbgn.pd
    assert momapy.sbgn.pd is not None


def test_sbgn_af_import():
    """Test that sbgn.af module can be imported."""
    import momapy.sbgn.af
    assert momapy.sbgn.af is not None


def test_sbgn_utils_import():
    """Test that sbgn.utils module can be imported."""
    import momapy.sbgn.utils
    assert momapy.sbgn.utils is not None
