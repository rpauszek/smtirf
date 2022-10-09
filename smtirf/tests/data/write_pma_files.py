import numpy as np
import tifffile
from pathlib import Path


def write_pma_data(savebase, traces, pks, img, n_frames, n_spots, log_params):
    """Write files associated with .pma movie"""
    filename = _write_traces_file(savebase, n_frames, n_spots, traces)
    _write_pks_file(savebase, pks)
    _write_tif_file(savebase, img)
    _write_log_file(savebase, **log_params)
    return filename


def _write_traces_file(savebase, n_frames, n_spots, traces):
    savename = savebase.with_suffix(".traces")
    data = np.vstack(traces).T
    with open(savename, "wb") as F:
        F.write(np.array([n_frames], dtype=np.int32).tobytes(order="C"))
        F.write(np.array([n_spots * 2], dtype=np.int16).tobytes(order="C"))
        F.write(data.astype(np.int16).tobytes(order="C"))
    return savename


def _write_pks_file(savebase, peaks):
    savename = savebase.with_suffix(".pks")
    peaks = np.vstack(peaks)  # spot coordinates
    ind = np.arange(peaks.shape[0])  # indices
    off = np.zeros(peaks.shape[0])  # baseline offset corrected

    fmt = ("%d", "%0.3f", "%0.3f", "%0.2e")
    data = np.hstack((ind[:, np.newaxis], peaks, off[:, np.newaxis]))
    np.savetxt(savename, data, fmt=fmt, delimiter="\t")


def _write_tif_file(savebase, image):
    savename = Path(savebase.parent) / (savebase.stem + "_ave.tif")
    with tifffile.TiffWriter(savename) as tif:
        tif.write(image)


def _write_log_file(savebase, gain, data_scaler, frame_length, record_date):
    savename = savebase.with_suffix(".log")
    with open(savename, "w") as F:
        F.write("CCD Gain\n")
        F.write(f"{gain}\n")
        F.write("Exposure Time (msec)\n")
        F.write(f"{frame_length}\n")
        F.write("Filming Date and Time\n")
        F.write(f"{record_date}\n")
        F.write("Data Scaler\n")
        F.write(f"{data_scaler}\n")


if __name__ == "__main__":
    from simulate import simulate_fret_experiment
    from datetime import datetime

    params = {
        "n_frames": 500,
        "n_spots": 5,
        "log_params": {
            "gain": 300,
            "data_scaler": 800,
            "frame_length": 100,
            "record_date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        },
    }

    sp, traces, pks, image = simulate_fret_experiment(3, 500, 5)
    write_pma_data(Path("./test_K3"), traces, pks, image, **params)
