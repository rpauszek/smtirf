from pathlib import Path

from . import pma


def load_from_pma(filename, *, savename=None):
    filename = Path(filename)
    savename = filename.with_suffix(".smtrc") if savename is None else Path(savename)

    traces = pma._read_traces(filename.with_suffix(".traces"))
    coordinates = pma._read_pks(filename.with_suffix(".pks"))
    log = pma._read_log(filename.with_suffix(".log"))

    print(log)
