from pathlib import Path

from . import pma


def load_from_pma(filename, *, savename=None):
    filename = Path(filename)
    savename = filename.with_suffix(".smtrc") if savename is None else Path(savename)
    coordinates = pma._read_pks(filename.with_suffix(".pks"))
