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

# ==============================================================================
# public API
# ==============================================================================
def read(filename):
    output = _read_traces(filename)
    output["pks"] = _read_pks(filename)
    log = _read_log(filename)
    output = {**output, **log}
    output["img"] = _read_tif(filename)
    return output



# ==============================================================================
# private API
# ==============================================================================
def _read_traces(filename):
    filename, ext = os.path.splitext(filename)
    with open(filename + ".traces", "rb") as F:
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
    filename, ext = os.path.splitext(filename)
    with open(filename + ".pks", "r") as F:
        data = np.loadtxt(F)
    # [dx, dy, ax, ay]
    return np.hstack((data[::2, 1:-1], data[1::2, 1:-1]))

def _read_log(filename):
    output = {"info": {"filename": filename}}
    filename, ext = os.path.splitext(filename)
    with open(filename + ".log", "r") as f:
        for line in f:
            if "Gain" in line:
                output["info"]["ccdGain"] = int(next(f))
            elif "Exposure Time" in line:
                output["frameLength"] = float(next(f))/1000 # msec => sec
            elif "Filming Date and Time" in line:
                output["recordTime"] = datetime.strptime(next(f).strip(), "%a %b %d %H:%M:%S %Y")
            elif "Data Scaler" in line:
                output["info"]["dataScaler"] = int(next(f))
    return output

def _read_tif(filename):
    filename, ext = os.path.splitext(filename)
    img = imread(filename + "_ave.tif")
    img = color.rgb2gray(img)
    return img
