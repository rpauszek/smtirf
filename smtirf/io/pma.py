# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> io >> pma
"""
import numpy as np
from skimage.io import imread
from skimage import color
from datetime import datetime
import os.path
# from pathlib import Path

# ==============================================================================
# public API
# ==============================================================================
def read(filename):
    """ import data from IDL-generated files of .pma movies
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


# ==============================================================================
# private API
# ==============================================================================
def _read_traces(filename):
    with open(filename.with_suffix(".traces"), "rb") as F:
        nFrames = np.fromfile(F, dtype=np.int32, count=1)[0]
        nRecords = np.fromfile(F, dtype=np.int16, count=1)[0]
        # check number of traces is integer
        if (nRecords % 1) != 0:
            raise ValueError(f"non-integer number of traces in dataset [{nRecords}]")
        else:
            nTraces = (nRecords/2).astype(np.int)
        # read data, records as columns
        data = np.fromfile(F, dtype=np.int16, count=-1).reshape((nFrames, nRecords), order="C")
    # split channels, traces as rows
    D0 = data[:, 0::2].T
    A0 = data[:, 1::2].T
    # default signal state label
    S0 = np.zeros((nTraces, nFrames)).astype(np.int)
    # default HMM statepath
    SP = np.ones((nTraces, nFrames)).astype(np.int) * -1
    return {"D0":D0, "A0":A0, "S0":S0, "SP":SP, "nTraces":nTraces, "nFrames":nFrames}

def _read_pks(filename):
    with open(filename.with_suffix(".pks"), "r") as F:
        data = np.loadtxt(F)
    # [dx, dy, ax, ay]
    return np.hstack((data[::2, 1:-1], data[1::2, 1:-1]))

def _read_log(filename):
    info = {"filename": str(filename)}
    log = {}
    with open(filename.with_suffix(".log"), "r") as f:
        for line in f:
            if "Gain" in line:
                info["ccdGain"] = int(next(f))
            elif "Exposure Time" in line:
                log["frameLength"] = float(next(f))/1000 # msec => sec
            elif "Filming Date and Time" in line:
                log["recordTime"] = datetime.strptime(next(f).strip(), "%a %b %d %H:%M:%S %Y")
            elif "Data Scaler" in line:
                info["dataScaler"] = int(next(f))
    return log, info

def _read_tif(filename):
    filename = filename.parent / (filename.stem + "_ave.tif")
    return color.rgb2gray(imread(filename))
