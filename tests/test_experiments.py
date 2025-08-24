from smtirf import Experiment
from smtirf.traces import Trace


def test_experiment(smtrc_file, mock_data):
    expt = Experiment(smtrc_file)
    assert len(expt) == mock_data.movie_metadata.n_traces
    assert expt.n_selected == 0

    trace = expt[0]
    assert isinstance(trace, Trace)
    trace.set_selected(True)
    assert expt.n_selected == 1

    expt.select_all()
    assert expt.n_selected == mock_data.movie_metadata.n_traces

    expt.select_none()
    assert expt.n_selected == 0
