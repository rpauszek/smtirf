from datetime import datetime

import numpy as np
from skimage import color
from skimage.io import imread

from .detail import Coordinates, RawTrace


def read(filename):
    """import data from IDL-generated files of .pma movies
    N traces of length T frames
    output = {
        D0          : raw donor (ch1) signal [NxT]
        A0          : raw acceptor (ch2) signal [NxT]
        S0          : initial signal state-labels [NxT] -> 0
        SP          : initial state-path [NxT] -> -1
        nTraces     : N
        nFrames     : T
        pks         : spot coordinates (ch1_x, ch1_y, ch2_x, ch2_y) [Nx4]
        info =      {filename   : original .trace file path
                     nTraces    : N
                     nFrames    : T
                     ccdGain    : camera gain
                     dataScaler : PMA data scaler option
                    }
        frameLength : camera integration time, sec
        recordTime  : recording timestamp -> datetime instance
        img         : static average image (first 10 frames, 512x512 pixels)
    }
    """
    output = _read_traces(filename)
    output["pks"] = _read_pks(filename)
    log, info = _read_log(filename)
    info["nTraces"] = output.pop("nTraces")
    info["nFrames"] = output.pop("nFrames")
    output["info"] = info
    output = {**output, **log}
    output["img"] = _read_tif(filename)
    return output


def _read_traces(filename):
    with open(filename.with_suffix(".traces"), "rb") as F:
        n_frames = np.fromfile(F, dtype=np.int32, count=1)[0]
        n_records = np.fromfile(F, dtype=np.int16, count=1)[0]
        # check number of traces is integer
        if (n_records % 1) != 0:
            raise ValueError(f"non-integer number of traces in dataset [{n_records}]")

        # read data, records as columns
        data = np.fromfile(F, dtype=np.int16, count=-1).reshape(
            (n_frames, n_records), order="C"
        )

    # split channels, traces as rows
    donor_traces = data[:, 0::2].T
    acceptor_traces = data[:, 1::2].T
    return [RawTrace(d, a) for d, a in zip(donor_traces, acceptor_traces)]


def _read_pks(filename):
    with open(filename, "r") as file:
        data = np.loadtxt(file, dtype=float)
    return [Coordinates.from_array(line) for line in data]


def _read_log(filename):
    info = {"filename": str(filename)}
    log = {}
    with open(filename.with_suffix(".log"), "r") as f:
        for line in f:
            if "Gain" in line:
                info["ccdGain"] = int(next(f))
            elif "Exposure Time" in line:
                log["frameLength"] = float(next(f)) / 1000  # msec => sec
            elif "Filming Date and Time" in line:
                log["recordTime"] = datetime.strptime(
                    next(f).strip(), "%a %b %d %H:%M:%S %Y"
                )
            elif "Data Scaler" in line:
                info["dataScaler"] = int(next(f))
    return log, info


def _read_tif(filename):
    filename = filename.parent / (filename.stem + "_ave.tif")
    image = imread(filename)
    return image if image.ndim == 2 else color.rgb2gray(image)
