"""Tests for momapy.animating module."""
import pytest
import momapy.core
import momapy.geometry

# Skip all tests in this module if ffmpeg is not available
pytest.importorskip("ffmpeg")
import momapy.animating


@pytest.fixture
def sample_animator(sample_layout):
    """Create a sample Animator for testing."""
    return momapy.animating.Animator(layout=sample_layout, fps=30)


def test_animator_creation(sample_layout):
    """Test creating an Animator."""
    animator = momapy.animating.Animator(layout=sample_layout)
    assert animator.layout is sample_layout
    assert animator.fps == 60  # default fps

    animator2 = momapy.animating.Animator(layout=sample_layout, fps=30)
    assert animator2.fps == 30


def test_animator_initialization(sample_animator):
    """Test that Animator initializes properly."""
    assert sample_animator._flimages is not None
    assert sample_animator._n_images == 0


def test_animator_mseconds_calculation(sample_animator):
    """Test mseconds calculation."""
    # Test that mseconds method exists and doesn't crash with simple call
    # Note: We're not actually building the animation to avoid file I/O
    initial_images = sample_animator._n_images
    # We can't fully test this without file I/O, but we can verify the method exists
    assert hasattr(sample_animator, 'mseconds')
    assert callable(sample_animator.mseconds)


def test_animator_frames_method(sample_animator):
    """Test that frames method exists."""
    assert hasattr(sample_animator, 'frames')
    assert callable(sample_animator.frames)


def test_animator_build_method(sample_animator):
    """Test that build method exists."""
    assert hasattr(sample_animator, 'build')
    assert callable(sample_animator.build)
