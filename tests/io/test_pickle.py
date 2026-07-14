"""Tests for momapy.io.pickle round-tripping of maps and bare objects."""

import pytest

import momapy.core.layout
import momapy.geometry
import momapy.io.pickle
import momapy.sbgn.pd


def _write(obj, tmp_path):
    file_path = tmp_path / "obj.pkl"
    momapy.io.pickle.PickleWriter.write(obj, file_path)
    return file_path


class TestPickleBareModel:
    """A bare Model pickle round-trips and rejects incompatible return types."""

    def test_round_trip_as_model(self, tmp_path):
        """A bare Model read back with return_type='model' is returned as-is."""
        model = momapy.sbgn.pd.SBGNPDModel()
        file_path = _write(model, tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, return_type="model")
        assert isinstance(result.obj, momapy.sbgn.pd.SBGNPDModel)

    def test_as_map_raises(self, tmp_path):
        """Requesting a map from a bare Model pickle raises ValueError."""
        model = momapy.sbgn.pd.SBGNPDModel()
        file_path = _write(model, tmp_path)
        with pytest.raises(ValueError):
            momapy.io.pickle.PickleReader.read(file_path, return_type="map")


class TestPickleBareLayout:
    """A bare Layout pickle round-trips and rejects incompatible return types."""

    def _layout(self):
        return momapy.core.layout.Layout(
            position=momapy.geometry.Point(0, 0), width=10, height=10
        )

    def test_round_trip_as_layout(self, tmp_path):
        """A bare Layout read back with return_type='layout' is returned as-is."""
        file_path = _write(self._layout(), tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, return_type="layout")
        assert isinstance(result.obj, momapy.core.layout.Layout)

    def test_as_model_raises(self, tmp_path):
        """Requesting a model from a bare Layout pickle raises ValueError."""
        file_path = _write(self._layout(), tmp_path)
        with pytest.raises(ValueError):
            momapy.io.pickle.PickleReader.read(file_path, return_type="model")
