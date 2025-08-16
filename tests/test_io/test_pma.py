from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np


def test_read_traces():
    n_frames = 4
    n_records = 6
    fake_data = (
        np.arange(n_frames * n_records, dtype=np.int16).reshape((n_records, n_frames)).T
    )  # traces as columns

    def fromfile_side_effect(_, dtype, count):
        if dtype == np.int32 and count == 1:
            return np.array([n_frames], dtype=np.int32)
        elif dtype == np.int16 and count == 1:
            return np.array([n_records], dtype=np.int16)
        elif dtype == np.int16 and count == -1:
            return fake_data.flatten(order="C")
        else:
            raise ValueError("Unexpected call")

    dummy_file = MagicMock()
    dummy_path = Path("dummyfile.traces")

    with patch("builtins.open", return_value=dummy_file, create=True), patch(
        "numpy.fromfile", side_effect=fromfile_side_effect
    ):
        from smtirf.io.pma import _read_traces

        results = _read_traces(dummy_path)
        n_traces = len(results)

        assert n_traces == n_records // 2
        for k in range(n_traces):
            print(results[k])
            np.testing.assert_array_equal(results[k].donor, fake_data[:, k * 2])
            np.testing.assert_array_equal(results[k].acceptor, fake_data[:, k * 2 + 1])


def test_read_pks():
    fake_pks_str = """
       1    15.000   311.000  6.34e+000
       2   268.500   313.000  5.01e+000
    """
    expected_coordinates = [[1.0, 15.0, 311.0, 6.34], [2.0, 268.5, 313.0, 5.01]]

    with patch("builtins.open", return_value=StringIO(fake_pks_str)):
        from smtirf.io.pma import _read_pks

        results = _read_pks(Path("dummy.pks"))

        assert len(results) == 2
        for coord, expected in zip(results, expected_coordinates):
            assert coord.donor.x == expected[0]
            assert coord.donor.y == expected[1]
            assert coord.acceptor.x == expected[2]
            assert coord.acceptor.y == expected[3]
