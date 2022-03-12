import numpy as np
import tifffile
from pathlib import Path


def write_pma_data(savebase, traces, pks, img, T, N, log_params):
    """Write files associated with .pma movie"""
    filename = _write_traces_file(savebase, T, N, traces)
    # _write_pks_file(savebase, pks)
    # _write_tif_file(savebase, img)
    _write_log_file(savebase, **log_params)
    return filename


def _write_traces_file(savebase, T, N, traces):
    savename = savebase.with_suffix(".traces")
    data = np.vstack(traces).T
    with open(savename, "wb") as F:
        F.write(np.array([T], dtype=np.int32).tobytes(order="C"))
        F.write(np.array([N * 2], dtype=np.int16).tobytes(order="C"))
        F.write(data.astype(np.int16).tobytes(order="C"))
    return savename


def _write_pks_file(savebase, pks):
    savename = savebase.with_suffix(".pks")
    pks = np.vstack(pks)  # spot coordinates
    ind = np.arange(pks.shape[0])  # indices
    off = np.zeros(pks.shape[0])  # baseline offset corrected

    fmt = ("%d", "%0.1f", "%0.1f", "%0.4f")
    data = np.hstack((ind[:, np.newaxis], pks, off[:, np.newaxis]))
    np.savetxt(savename, data, fmt=fmt, delimiter="\t")


def _write_tif_file(savebase, img):
    savename = Path(savebase.parent) / (savebase.stem + "_ave.tif")
    with tifffile.TiffWriter(savename) as tif:
        tif.save(img)


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
    import simulate
    from datetime import datetime

    params = {
        "T": 1000,
        "N": 5,
        "log_params": {
            "gain": 300,
            "data_scaler": 800,
            "frame_length": 100,
            "record_date": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        },
    }

    K = 3
    pi = np.ones(K) / K
    A = (np.eye(K) * 10) + np.ones((K, K))
    A = A / A.sum(axis=1)[:, np.newaxis]
    sp = simulate.simulate_statepath(K, pi, A, params["T"])

    frame_time_sec = 0.100
    bleach_lifetime = 80
    bleach_lifetime_frames = bleach_lifetime / frame_time_sec

    traces = []
    for i in range(params["N"]):
        print(i)
        fret, donor, acceptor, _ = simulate.simulate_fret_experiment(
            sp, np.linspace(0, 1, K), 300, 30, bleach_lifetime_frames
        )
        traces.append((donor, acceptor))

    pks, img = None, None
    write_pma_data(Path("./test_K3"), traces, pks, img, **params)
