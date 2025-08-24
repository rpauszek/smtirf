from collections import namedtuple

import numpy as np
import pytest

from smtirf import Experiment
from smtirf.traces import Trace

USE_TRACE_INDEX = 0


@pytest.fixture
def mock_trace(smtrc_file):
    expt = Experiment(smtrc_file)
    return expt[USE_TRACE_INDEX]


@pytest.fixture
def expected_signals(mock_data):
    signal = namedtuple("ExpectedSignal", ("raw", "offset", "baselined", "corrected"))

    # todo: not implemented yet, update when added to experiment
    bleed = 0.05
    gamma = 1

    trace = mock_data.traces[USE_TRACE_INDEX]

    raw = trace.donor
    offset = 5
    baselined = raw - offset
    corrected = baselined * gamma
    donor = signal(raw, offset, baselined, corrected)

    raw = trace.acceptor
    offset = 10
    baselined = raw - offset
    corrected = baselined - (donor.baselined * bleed)
    acceptor = signal(raw, offset, baselined, corrected)

    expected_time = (
        np.arange(mock_data.movie_metadata.n_frames)
        * mock_data.movie_metadata.frame_length
    )

    return donor, acceptor, expected_time


def test_trace_basic_properties(mock_trace, mock_data):
    trace = mock_trace
    assert str(trace) == r"Trace	ID=20250824T163642_0000	selected=False"
    assert len(trace) == mock_data.movie_metadata.n_frames
    assert trace.frame_length == mock_data.movie_metadata.frame_length


def test_trace_selection(mock_trace):
    trace = mock_trace
    assert not trace.is_selected
    trace.toggle_selected()
    assert trace.is_selected
    trace.toggle_selected()
    assert not trace.is_selected

    trace.set_selected(True)
    assert trace.is_selected
    trace.set_selected(False)
    assert not trace.is_selected

    with pytest.raises(ValueError, match="value must be of type bool."):
        trace.set_selected(42)


def test_trace_data(mock_trace, expected_signals):
    trace = mock_trace
    donor, acceptor, time = expected_signals

    np.testing.assert_equal(trace.raw.time, time)
    np.testing.assert_equal(trace.raw.donor, donor.raw)
    np.testing.assert_equal(trace.raw.acceptor, acceptor.raw)
    np.testing.assert_equal(trace.raw.total, donor.raw + acceptor.raw)
    np.testing.assert_almost_equal(
        trace.raw.fret,
        acceptor.raw / (donor.raw + acceptor.raw),
    )

    trace.set_offsets([donor.offset, acceptor.offset])

    np.testing.assert_equal(trace._baselined_dispatcher.time, time)
    np.testing.assert_almost_equal(trace._baselined_dispatcher.donor, donor.baselined)
    np.testing.assert_almost_equal(
        trace._baselined_dispatcher.acceptor, acceptor.baselined
    )

    np.testing.assert_equal(trace.corrected.time, time)
    np.testing.assert_equal(trace.corrected.donor, donor.corrected)
    np.testing.assert_equal(trace.corrected.acceptor, acceptor.corrected)


def test_trace_limits(mock_trace, expected_signals):
    trace = mock_trace
    donor, acceptor, time = expected_signals

    # ! todo: need better mock data for handling combinations and not re-doing this all the time
    trace.set_offsets([donor.offset, acceptor.offset])

    np.testing.assert_equal(trace.limits, [0, 5])
    np.testing.assert_equal(trace.time, time)
    np.testing.assert_equal(trace.donor, donor.corrected)
    np.testing.assert_equal(trace.acceptor, acceptor.corrected)

    limits = [1, 3]
    trace.set_limits(*limits)

    np.testing.assert_equal(trace.limits, limits)
    np.testing.assert_equal(trace.time, time[slice(*limits)])
    np.testing.assert_equal(trace.donor, donor.corrected[slice(*limits)])
    np.testing.assert_equal(trace.acceptor, acceptor.corrected[slice(*limits)])


# todo: test with_statepath_update ? or inherently tested with decorated methods ?
