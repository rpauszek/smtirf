from pathlib import Path

from . import pma


def load_from_pma(filename, *, savename=None):
    filename = Path(filename)
    savename = filename.with_suffix(".smtrc") if savename is None else Path(savename)

    required_files = {
        "traces": filename.with_suffix(".traces"),
        "peaks": filename.with_suffix(".pks"),
        "log": filename.with_suffix(".log"),
        "image": filename.with_name(f"{filename.stem}_ave.tif"),
    }

    missing_files = [str(path) for path in required_files.values() if not path.exists()]
    if len(missing_files) > 0:
        missing_string = ",\n".join(missing_files)
        raise FileNotFoundError(f"Missing required file(s):\n{missing_string}")

    traces = pma._read_traces(required_files["traces"])
    peaks = pma._read_pks(required_files["peaks"])
    log = pma._read_log(required_files["log"])
    image = pma._read_tif(required_files["image"])
