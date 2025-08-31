import itertools
from pathlib import Path
from unittest.mock import patch

import pytest

from smtirf.io.import_dispatch import load_from_pma

# todo: test happy path!


def generate_missing_file_permutations():
    n = [(n_true, 4 - n_true) for n_true in range(1, 4)]
    items = [[True] * n_true + [False] * n_false for n_true, n_false in n]

    permutations = itertools.chain(
        *[set(itertools.permutations(item, 4)) for item in items]
    )
    return sorted(permutations)


MISSING_FILE_PERMUTATIONS = generate_missing_file_permutations()


@pytest.mark.parametrize("exists_flags", MISSING_FILE_PERMUTATIONS)
def test_load_from_pma_missing_files(exists_flags):
    filename = Path("experiment.traces")
    possible_filenames = (
        filename.with_suffix(".traces"),
        filename.with_suffix(".pks"),
        filename.with_suffix(".log"),
        Path(f"{filename.stem}_ave.tif"),
    )

    existing_files = {
        f for f, exists in zip(possible_filenames, exists_flags) if exists
    }
    missing_files = set(possible_filenames) - existing_files

    def fake_exists(path):
        return path in existing_files

    with patch("pathlib.Path.exists", fake_exists):
        with pytest.raises(FileNotFoundError) as excinfo:
            load_from_pma(filename)

    msg = str(excinfo.value)
    for filename in missing_files:
        assert str(filename) in msg

    n_breaks = msg.count("\n")
    assert n_breaks == 4 - sum(exists_flags)


def test_unknown_experiment_type(tmp_path):
    filename = Path("experiment.traces")
    savename = Path(tmp_path) / "bad_experiment.smtrc"

    with pytest.raises(ValueError) as e:
        load_from_pma(filename, experiment_type="bozo")
    assert str(e.value) == "experiment type must be in ('fret', 'twocolor'); got bozo"
