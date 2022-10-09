from smtirf import Experiment


def test_from_pma(fret_pma_file):
    filename_base, params, statepaths = fret_pma_file
    experiment = Experiment.from_pma(filename_base.with_suffix(".traces"), "fret")

    assert len(experiment) == params["n_spots"]
    assert str(experiment) == "FretExperiment\t0/5 selected"


def test_load(fret_pma_file):
    filename_base, params, statepaths = fret_pma_file
    experiment = Experiment.load(filename_base.with_suffix(".smtrc"))

    assert len(experiment) == params["n_spots"]
    assert str(experiment) == "FretExperiment\t0/5 selected"


def test_selection(fret_pma_file):
    filename_base, params, statepaths = fret_pma_file
    experiment = Experiment.load(filename_base.with_suffix(".smtrc"))

    assert experiment.nSelected == 0

    experiment[2].toggle()
    assert experiment.nSelected == 1

    experiment[2].toggle()
    assert experiment.nSelected == 0

    experiment.select_all()
    assert experiment.nSelected == 5

    experiment.select_none()
    assert experiment.nSelected == 0


def test_sorting(fret_pma_file):
    def strip_trace_ids(experiment):
        return [int(str(trace._id)[-4:]) for trace in experiment]

    filename_base, params, statepaths = fret_pma_file
    experiment = Experiment.load(filename_base.with_suffix(".smtrc"))
    assert strip_trace_ids(experiment) == [0, 1, 2, 3, 4]

    experiment.sort("corrcoef")
    assert strip_trace_ids(experiment) == [3, 1, 2, 4, 0]

    experiment.sort("cluster")
    assert strip_trace_ids(experiment) == [3, 1, 2, 4, 0]

    experiment.sort("selected")
    assert strip_trace_ids(experiment) == [3, 1, 2, 4, 0]

    experiment.sort("index")
    assert strip_trace_ids(experiment) == [0, 1, 2, 3, 4]

    experiment[2].toggle()
    experiment.sort("selected")
    assert strip_trace_ids(experiment) == [2, 0, 1, 3, 4]
