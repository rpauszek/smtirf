from smtirf import Experiment


def test_bozo(fret_pma_file):
    filename_base, statepaths = fret_pma_file
    e = Experiment.from_pma(filename_base.with_suffix(".traces"), "fret")
