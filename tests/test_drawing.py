"""Tests for momapy.drawing module."""
import pytest
import momapy.drawing
import momapy.coloring


def test_none_value_singleton():
    """Test NoneValue singleton."""
    assert momapy.drawing.NoneValue is not None
    assert isinstance(momapy.drawing.NoneValue, momapy.drawing.NoneValueType)


def test_none_value_copy():
    """Test NoneValue copy operations."""
    import copy

    nv1 = momapy.drawing.NoneValue
    nv2 = copy.copy(nv1)
    nv3 = copy.deepcopy(nv1)

    assert nv1 is nv2
    assert nv1 is nv3


def test_none_value_equality():
    """Test NoneValue equality."""
    nv1 = momapy.drawing.NoneValue
    nv2 = momapy.drawing.NoneValue

    assert nv1 == nv2
    assert not (nv1 != nv2)


def test_drop_shadow_effect_creation():
    """Test creating a DropShadowEffect."""
    effect = momapy.drawing.DropShadowEffect(
        dx=5.0,
        dy=5.0,
        std_deviation=2.0,
        flood_opacity=0.5,
        flood_color=momapy.coloring.black,
    )

    assert effect.dx == 5.0
    assert effect.dy == 5.0
    assert effect.std_deviation == 2.0
    assert effect.flood_opacity == 0.5


def test_drop_shadow_effect_to_compat():
    """Test DropShadowEffect to_compat method."""
    effect = momapy.drawing.DropShadowEffect(
        dx=5.0,
        dy=5.0,
        std_deviation=2.0,
    )

    compat_effects = effect.to_compat()

    assert isinstance(compat_effects, list)
    assert len(compat_effects) > 0
    # Should return multiple effects
    assert all(isinstance(e, momapy.drawing.FilterEffect) for e in compat_effects)


def test_filter_effect_input_enum():
    """Test FilterEffectInput enum."""
    assert momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC is not None
    assert momapy.drawing.FilterEffectInput.SOURCE_ALPHA is not None
    assert isinstance(momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC, momapy.drawing.FilterEffectInput)


def test_composition_operator_enum():
    """Test CompositionOperator enum."""
    assert momapy.drawing.CompositionOperator.OVER is not None
    assert momapy.drawing.CompositionOperator.IN is not None
    assert isinstance(momapy.drawing.CompositionOperator.OVER, momapy.drawing.CompositionOperator)


def test_composite_effect_creation():
    """Test creating a CompositeEffect."""
    effect = momapy.drawing.CompositeEffect(
        in_=momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC,
        in2=momapy.drawing.FilterEffectInput.SOURCE_ALPHA,
        operator=momapy.drawing.CompositionOperator.IN,
    )

    assert effect.in_ == momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC
    assert effect.in2 == momapy.drawing.FilterEffectInput.SOURCE_ALPHA
    assert effect.operator == momapy.drawing.CompositionOperator.IN
