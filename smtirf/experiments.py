import json
from datetime import datetime
from pathlib import Path

import h5py
import numpy as np

import smtirf

from . import SMJsonDecoder, SMJsonEncoder, SMMovieList, SMTraceID, io, traces
from .detail.metadata import MovieMetadata
from .results import Results


class Experiment:
    def __init__(self, filename):
        # self._movies = movies
        # self._traces = traces
        # self.frameLength = frameLength
        # self.comments = comments
        # self.results = Results(self) if results is None else Results(self, **results)

        self._file_handle = h5py.File(filename, "r")

        self._movies = {
            key: MovieMetadata._from_group(group)
            for key, group in self._file_handle["movies"].items()
        }
        print(self._movies)

    def save(self, savename):
        Experiment.write_to_hdf(savename, self)

    def __getitem__(self, index):
        return self._traces[index]

    def __len__(self):
        return len(self._traces)

    def __str__(self):
        return f"{self.__class__.__name__}\t{self.nSelected}/{len(self)} selected"

    @property
    def nSelected(self):
        return sum(1 for trc in self if trc.isSelected)

    def detect_baseline(
        self,
        baselineCutoff=100,
        nComponents=5,
        nPoints=1e4,
        maxIter=50,
        tol=1e-3,
        printWarnings=False,
        where="first",
        correctOffsets=True,
    ):
        M = smtirf.util.AutoBaselineModel(self, baselineCutoff=baselineCutoff)
        M.train_gmm(nComponents=nComponents, nPoints=nPoints)
        M.train_hmm(maxIter=maxIter, tol=tol, printWarnings=printWarnings)
        for trc, sp in zip(self, M.SP):
            trc.set_signal_labels(sp, where=where, correctOffsets=correctOffsets)

    def sort(self, key="corrcoef"):
        if key == "corrcoef":
            fcn = lambda x: x.corrcoef
            reverse = False  # ascending
        elif key == "index":
            fcn = lambda x: str(x._id)
            reverse = False  # ascending
        elif key == "cluster":
            fcn = lambda x: str(x.clusterIndex)
            reverse = False  # ascending
        elif key == "selected":
            fcn = lambda x: x.isSelected
            reverse = True  # descending
        else:
            raise KeyError(f"cannot sort by key '{key}'")
        self._traces.sort(key=fcn, reverse=reverse)

    def select_all(self):
        for trc in self:
            trc.isSelected = True

    def select_none(self):
        for trc in self:
            trc.isSelected = False

    def update_results(self):
        # self.results = smtirf.results.Results(self)
        self.results.hist.calculate()
        self.results.tdp.calculate()
