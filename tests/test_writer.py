from datetime import datetime
from pathlib import Path

import h5py
import numpy as np
import pytest

from smtirf.detail.definitions import Coordinates, Point, RawTrace
from smtirf.detail.metadata import MovieMetadata
from smtirf.detail.writer import write_movie_to_hdf


@pytest.fixture
def traces():
    return [
        RawTrace(np.arange(0, 5), np.arange(5, 10)),
        RawTrace(np.arange(10, 15), np.arange(15, 20)),
    ]


@pytest.fixture
def peaks():
    return [
        Coordinates(Point(0, 0), Point(1, 1)),
        Coordinates(Point(2, 2), Point(3, 3)),
    ]


@pytest.fixture
def snapshot():
    return np.random.poisson(50, size=(10, 10))


@pytest.fixture
def timestamp():
    return datetime(year=2025, month=8, day=19, hour=14, minute=30, second=0)


@pytest.fixture
def make_movie_metadata(timestamp):
    def wrapped(log, include_data_scaler=True):
        return MovieMetadata(
            n_traces=2,
            n_frames=5,
            src_filename="bozo.traces",
            timestamp=timestamp,
            frame_length=0.1,
            ccd_gain=300,
            data_scaler=1500 if include_data_scaler else None,
            log=log,
        )

    return wrapped


def test_write_movie_to_hdf(
    tmp_path, traces, peaks, snapshot, timestamp, make_movie_metadata
):
    savename = Path(tmp_path) / "imported_movie.smtrc"
    metadata = make_movie_metadata(
        log={"key1": "value1", "key2": 50, "key3": timestamp}
    )
    write_movie_to_hdf(savename, traces, peaks, metadata, snapshot)
    with h5py.File(savename, "r") as hf:
        assert hf.attrs["date_modified"]
        assert hf.attrs["smtirf_version"] == "0.1.5"
        assert hf.attrs["smtrc_version"] == "2.0.0"

        group = hf[f"movies/movie_{metadata.uid}"]

        trace_ids = group["trace_ids"][:]
        assert len(trace_ids) == 2
        assert trace_ids[0].decode("utf-8") == f"{metadata.uid}_0000"
        assert trace_ids[1].decode("utf-8") == f"{metadata.uid}_0001"

        donor_data = group["traces/donor_traces"][:]
        assert donor_data.shape == (2, 5)
        np.testing.assert_equal(
            donor_data, np.vstack([trace.donor for trace in traces])
        )

        acceptor_data = group["traces/acceptor_traces"][:]
        assert acceptor_data.shape == (2, 5)
        np.testing.assert_equal(
            acceptor_data, np.vstack([trace.acceptor for trace in traces])
        )

        conf_sp_data = group["statepaths/conformation"][:]
        assert conf_sp_data.shape == (2, 5)
        np.testing.assert_equal(conf_sp_data, np.full((2, 5), -1))

        phot_sp_data = group["statepaths/photophysics"][:]
        assert phot_sp_data.shape == (2, 5)
        np.testing.assert_equal(phot_sp_data, np.zeros((2, 5)))

        snapshot = group["snapshot"][:]
        assert snapshot.shape == (10, 10)


def test_write_movie_to_hdf_no_snapshot(
    tmp_path, traces, peaks, snapshot, timestamp, make_movie_metadata
):
    savename = Path(tmp_path) / "imported_movie_no_snapshot.smtrc"
    metadata = make_movie_metadata(log={"1": 1})
    write_movie_to_hdf(savename, traces, peaks, metadata)

    with h5py.File(savename, "r") as hf:
        assert f"movies/movie_{metadata.uid}/snapshot" not in hf


def test_movie_metadata_written(
    tmp_path, traces, peaks, snapshot, timestamp, make_movie_metadata
):
    # normal metadata, log included with proper type serialization
    savename = Path(tmp_path) / "imported_movie.smtrc"
    metadata = make_movie_metadata(
        log={"key1": "value1", "key2": 50, "key3": timestamp, "key4": None}
    )
    write_movie_to_hdf(savename, traces, peaks, metadata, snapshot)
    with h5py.File(savename, "r") as hf:
        group = hf[f"movies/movie_{metadata.uid}"]
        assert group.attrs["ccd_gain"] == 300
        assert group.attrs["data_scaler"] == 1500
        assert group.attrs["frame_length"] == 0.1
        assert group.attrs["n_frames"] == 5
        assert group.attrs["n_traces"] == 2
        assert group.attrs["src_filename"] == "bozo.traces"
        assert group.attrs["timestamp"] == "2025-08-19T14:30:00"
        assert (
            group.attrs["log"]
            == '{"key1":"value1","key2":50,"key3":"2025-08-19T14:30:00","key4":null}'
        )

    # no data scaler
    savename = Path(tmp_path) / "imported_movie_no_data_scaler.smtrc"
    metadata = make_movie_metadata(
        log={"key1": "value1", "key2": 50, "key3": timestamp}, include_data_scaler=False
    )
    write_movie_to_hdf(savename, traces, peaks, metadata, snapshot)
    with h5py.File(savename, "r") as hf:
        group = hf[f"movies/movie_{metadata.uid}"]
        assert "data_scaler" not in group.attrs

    # no log
    savename = Path(tmp_path) / "imported_movie_no_log.smtrc"
    metadata = make_movie_metadata(log={})
    write_movie_to_hdf(savename, traces, peaks, metadata, snapshot)
    with h5py.File(savename, "r") as hf:
        group = hf[f"movies/movie_{metadata.uid}"]
        assert group.attrs["log"] == r"{}"
