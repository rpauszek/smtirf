from pathlib import Path

import h5py

import smtirf

from .detail.metadata import MovieMetadata
from .detail.registry import TRACE_REGISTRY


class Experiment:
    def __init__(self, filename):
        self._file_handle = h5py.File(Path(filename), "r")
        self._experiment_type = self._file_handle.attrs["experiment_type"]

        self._movies = {
            key: MovieMetadata._from_group(group)
            for key, group in self._file_handle["movies"].items()
        }

        # todo: cleanup
        trace_class = TRACE_REGISTRY[self._experiment_type]
        self._traces = []
        for group in self._file_handle["movies"].values():
            trace_ids = group["trace_ids"][:]
            for uid in trace_ids:
                trace = trace_class(self._file_handle, uid.decode("utf-8"))
                self._traces.append(trace)

        # self.comments = comments
        # self.results = Results(self) if results is None else Results(self, **results)

    def save(self, savename):
        Experiment.write_to_hdf(savename, self)

    def __getitem__(self, index):
        return self._traces[index]

    def __len__(self):
        return len(self._traces)

    def __str__(self):
        return f"{self.__class__.__name__}\t{self.n_selected}/{len(self)} selected"

    @property
    def n_selected(self):
        return sum(1 for trace in self if trace.is_selected)

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
        for trc, sp in zip(self, M.SP, strict=False):
            trc.set_signal_labels(sp, where=where, correctOffsets=correctOffsets)

    def sort(self, key="corrcoef"):
        if key == "corrcoef":
            self._traces.sort(key=lambda x: x.corrcoef, reverse=False)
        elif key == "index":
            self._traces.sort(key=lambda x: str(x._id), reverse=False)
        elif key == "cluster":
            self._traces.sort(key=lambda x: str(x.clusterIndex), reverse=False)
        elif key == "selected":
            self._traces.sort(key=lambda x: x.isSelected, reverse=True)  # descending
        else:
            raise KeyError(f"cannot sort by key '{key}'")

    def select_all(self):
        for trace in self:
            trace.set_selected(True)

    def select_none(self):
        for trace in self:
            trace.set_selected(False)

    def update_results(self):
        # self.results = smtirf.results.Results(self)
        self.results.hist.calculate()
        self.results.tdp.calculate()
