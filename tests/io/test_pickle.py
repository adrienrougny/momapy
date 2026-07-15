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


class TestPickleReaderResultContract:
    """The pickle reader matches the native readers' ReaderResult contract."""

    def _map(self):
        model = momapy.sbgn.pd.SBGNPDModel()
        layout = momapy.core.layout.Layout(
            position=momapy.geometry.Point(0, 0), width=10, height=10
        )
        return momapy.sbgn.pd.SBGNPDMap(model=model, layout=layout)

    def _write_with_source_tables(self, obj, tmp_path):
        file_path = tmp_path / "obj.pkl"
        momapy.io.pickle.PickleWriter.write(
            obj,
            file_path,
            source_id_to_model_element={"m": {object()}},
            source_id_to_layout_element={"l": object()},
        )
        return file_path

    def test_layout_projection_nulls_model_source_table(self, tmp_path):
        """return_type='layout' nulls source_id_to_model_element (finding 27)."""
        file_path = self._write_with_source_tables(self._map(), tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, return_type="layout")
        assert result.source_id_to_model_element is None
        assert result.source_id_to_layout_element is not None

    def test_model_projection_nulls_layout_source_table(self, tmp_path):
        """return_type='model' nulls source_id_to_layout_element (finding 27)."""
        file_path = self._write_with_source_tables(self._map(), tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, return_type="model")
        assert result.source_id_to_layout_element is None
        assert result.source_id_to_model_element is not None

    def test_map_without_model_nulls_model_source_table(self, tmp_path):
        """with_model=False nulls source_id_to_model_element (finding 27)."""
        file_path = self._write_with_source_tables(self._map(), tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, with_model=False)
        assert result.obj.model is None
        assert result.source_id_to_model_element is None

    def test_id_to_element_rebuilt_from_projected_obj(self, tmp_path):
        """id_to_element is rebuilt from the projected obj (finding 28)."""
        map_ = self._map()
        file_path = _write(map_, tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path)
        assert result.id_to_element is not None
        obj = result.obj
        assert result.id_to_element[obj.id_] is obj
        assert result.id_to_element[obj.model.id_] is obj.model
        assert result.id_to_element[obj.layout.id_] is obj.layout

    def test_id_to_element_layout_projection_excludes_model(self, tmp_path):
        """A layout projection's id_to_element holds only layout-side ids."""
        map_ = self._map()
        model_id = map_.model.id_
        file_path = _write(map_, tmp_path)
        result = momapy.io.pickle.PickleReader.read(file_path, return_type="layout")
        assert result.id_to_element is not None
        assert model_id not in result.id_to_element
        assert result.obj.id_ in result.id_to_element
