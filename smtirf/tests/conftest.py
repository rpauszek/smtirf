import pytest
import numpy as np
from datetime import datetime
from pathlib import Path

from smtirf import Experiment

from .data.simulate import simulate_fret_experiment
from .data.write_pma_files import write_pma_data


def fret_pma_parameters(n_frames, n_spots):
    return {
        "K": 3,
        "n_frames": n_frames,
        "n_spots": n_spots,
        "hmm_params": {
            "transition_diag": 10,
            "frame_length": 0.100,
            "signal_lifetime": 80,
            "total_intensity": 500,
            "channel_sigma": 30,
            "frame_size": 512,
            "channel_border": 20,
            "seed": 1234,
        },
        "log_params": {
            "gain": 300,
            "data_scaler": 800,
            "frame_length": 100,
            "record_date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        },
    }


def write_simulated_files(tmpdir_factory, filename, n_frames, n_spots):
    tmpdir = Path(str(tmpdir_factory.mktemp("smtirf")))
    savebase = tmpdir / filename
    params = fret_pma_parameters(n_frames, n_spots)

    statepaths, *data = simulate_fret_experiment(
        params["K"], params["n_frames"], params["n_spots"], **params["hmm_params"]
    )

    write_pma_data(
        savebase, *data, params["n_frames"], params["n_spots"], params["log_params"]
    )

    return savebase, params, statepaths


@pytest.fixture(scope="session")
def fret_pma_file(tmpdir_factory):
    return write_simulated_files(tmpdir_factory, "hel1", n_frames=1000, n_spots=5)


@pytest.fixture(scope="session")
def fret_short_file(tmpdir_factory):
    return write_simulated_files(tmpdir_factory, "short3", n_frames=25, n_spots=5)
