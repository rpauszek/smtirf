from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


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
            np.testing.assert_array_equal(results[k].channel_1, fake_data[:, k * 2])
            np.testing.assert_array_equal(results[k].channel_2, fake_data[:, k * 2 + 1])


def test_read_pks():
    fake_pks_str = """
       1     1.000     2.000  6.34e+000
       2     3.500     4.000  5.01e+000
       3     5.000     6.000  6.34e+000
       4     7.500     8.000  5.01e+000
    """
    expected_coordinates = [[1.0, 2.0, 3.5, 4.0], [5.0, 6, 7.5, 8.0]]

    with patch("builtins.open", return_value=StringIO(fake_pks_str)):
        from smtirf.io.pma import _read_pks

        results = _read_pks(Path("dummy.pks"))

        assert len(results) == 2
        for coord, expected in zip(results, expected_coordinates):
            assert coord.channel_1.x == expected[0]
            assert coord.channel_1.y == expected[1]
            assert coord.channel_2.x == expected[2]
            assert coord.channel_2.y == expected[3]


def test_read_log():
    fake_log = """
    Filming Date and Time
    Fri Aug 31 11:44:19 2018

    Server Index
    4434
    Frame Resolution
    512 512
    Background
    408
    Data Scaler
    800
    Byte Per Pixel
    1
    Camera Information
    Andor Ixon DU897_BV
    Camera Bit Depth
    14
    Gain
    300
    Exposure Time [ms]
    100.000
    Kinetic Cycle Time [ms]
    101.740
    Lag Beetween Images	[ms]
    1.740
    Active Area
    1 512 1 512
    """

    with patch("builtins.open", return_value=StringIO(fake_log)):
        from smtirf.io.pma import _read_log

        log = _read_log(Path("dummy.log"))
        assert "unknown_entries" not in log
        assert log["exposure_time_ms"] == 0.1


def test_read_log_unknown_entry():
    fake_log = """
    Filming Date and Time
    Fri Aug 31 11:44:19 2018

    Server Index
    4434
    Frame Resolution
    512 512
    Background
    408
    Data Scaler
    800
    Byte Per Pixel
    1
    Camera Information
    Andor Ixon DU897_BV
    Camera Bit Depth
    14
    Gain
    300
    Exposure Time [ms]
    100.000
    Kinetic Cycle Time [ms]
    101.740
    Lag Beetween Images	[ms]
    1.740
    Active Area
    1 512 1 512

    Some other thing
    42
    My extra key
    extra
    """

    with patch("builtins.open", return_value=StringIO(fake_log)):
        from smtirf.io.pma import _read_log

        with pytest.warns(UserWarning) as record:
            log = _read_log(Path("dummy.log"))

        assert (
            str(record[0].message) == 'unknown entry "Some other thing" found in log.'
        )
        assert str(record[1].message) == 'unknown entry "My extra key" found in log.'

        assert len(log["unknown_entries"]) == 2
        assert log["unknown_entries"]["some_other_thing"] == "42"
        assert "some_extra_thing" not in log

        assert log["unknown_entries"]["my_extra_key"] == "extra"
        assert "my_extra_key" not in log


def test_read_log_missing_entry():
    fake_log = """
    Filming Date and Time
    Fri Aug 31 11:44:19 2018

    Server Index
    4434
    Frame Resolution
    512 512
    Background
    408
    Byte Per Pixel
    1
    Camera Information
    Andor Ixon DU897_BV
    Camera Bit Depth
    14
    Gain
    300
    Exposure Time [ms]
    100.000
    Kinetic Cycle Time [ms]
    101.740
    Lag Beetween Images	[ms]
    1.740
    Active Area
    1 512 1 512
    """

    with patch("builtins.open", return_value=StringIO(fake_log)):
        from smtirf.io.pma import _read_log

        with pytest.raises(KeyError, match=r"missing required entries: Data Scaler."):
            _read_log(Path("dummy.log"))

    fake_log = """
    Filming Date and Time
    Fri Aug 31 11:44:19 2018

    Server Index
    4434
    Frame Resolution
    512 512
    Background
    408
    Byte Per Pixel
    1
    Camera Information
    Andor Ixon DU897_BV
    Camera Bit Depth
    14

    Exposure Time [ms]
    100.000
    Kinetic Cycle Time [ms]
    101.740
    Lag Beetween Images	[ms]
    1.740
    Active Area
    1 512 1 512
    """

    with patch("builtins.open", return_value=StringIO(fake_log)):
        from smtirf.io.pma import _read_log

        with pytest.raises(
            KeyError, match=r"missing required entries: Data Scaler, Gain."
        ):
            _read_log(Path("dummy.log"))
