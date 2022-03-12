import pytest
import numpy as np
from datetime import datetime
from pathlib import Path

from .data.simulate import simulate_fret_experiment
from .data.write_pma_files import write_pma_data


@pytest.fixture(scope="session")
def fret_pma_file(tmpdir_factory):
    tmpdir = Path(str(tmpdir_factory.mktemp("smtirf")))
    savebase = tmpdir / "hel1"

    params = {
        "K": 3,
        "n_frames": 1000,
        "n_spots": 5,
        "hmm_params": {
            "transition_diag": 10,
            "frame_length": 0.100,
            "signal_lifetime": 80,
            "total_intensity": 500,
            "channel_sigma": 30,
            "frame_size": 512,
            "channel_border": 20,
        },
        "log_params": {
            "gain": 300,
            "data_scaler": 800,
            "frame_length": 100,
            "record_date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        },
    }

    statepaths, *data = simulate_fret_experiment(
        params["K"], params["n_frames"], params["n_spots"], **params["hmm_params"]
    )

    write_pma_data(
        savebase, *data, params["n_frames"], params["n_spots"], params["log_params"]
    )

    return savebase, statepaths
