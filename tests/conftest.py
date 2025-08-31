from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from smtirf.detail.definitions import Coordinates, Point, RawTrace
from smtirf.detail.metadata import MovieMetadata
from smtirf.detail.writer import write_movie_to_hdf


@dataclass(frozen=True)
class MockData:
    traces: list[RawTrace]
    peaks: list[Coordinates]
    snapshot: np.ndarray
    movie_metadata: MovieMetadata


@pytest.fixture(scope="session")
def mock_data():
    n_traces = 6
    n_frames = 5
    traces = [
        RawTrace(
            np.arange(j, j + n_frames), np.arange(j + n_frames, j + (n_frames * 2))
        )
        for j in np.arange(n_traces) * n_frames * 2
    ]
    peaks = [Coordinates(Point(j, j), Point(j + 10, j)) for j in range(n_traces)]
    snapshot = np.random.poisson(50, size=(10, 10))
    movie_metadata = MovieMetadata(
        n_traces=n_traces,
        n_frames=n_frames,
        src_filename="bozo.traces",
        timestamp=datetime(year=2025, month=8, day=24, hour=16, minute=36, second=42),
        frame_length=0.1,
        ccd_gain=300,
        data_scaler=1500,
        log={},
    )
    return MockData(traces, peaks, snapshot, movie_metadata)


@pytest.fixture(scope="session")
def smtrc_file(tmp_path_factory, mock_data):
    base = tmp_path_factory.mktemp("data")
    filepath = base / "example.smtrc"

    write_movie_to_hdf(
        filepath,
        "fret",
        0.05,
        1,
        mock_data.traces,
        mock_data.peaks,
        mock_data.movie_metadata,
        mock_data.snapshot,
    )
    return filepath
