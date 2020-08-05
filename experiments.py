# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> experiments
"""
import numpy as np
from pathlib import Path
from . import SMTraceID, SMMovieList
from . import traces
from . import io

# ==============================================================================
# BASE EXPERIMENT CLASS
# ==============================================================================
class BaseExperiment():

    def __init__(self, movies, traces, frameLength, comments=""):
        self._movies = movies
        self._traces = traces
        self.frameLength = frameLength
        self.comments = comments

    def save(self, savename):
        Experiment.write_to_hdf(savename, self)

    # ==========================================================================
    # sequence interface
    # ==========================================================================
    def __getitem__(self, index):
        return self._traces[index]

    def __len__(self):
        return len(self._traces)

    def __str__(self):
        return f"{self.__class__.__name__}\t{self.nSelected}/{len(self)} selected"

    # ==========================================================================
    # properties
    # ==========================================================================
    @property
    def nSelected(self):
        return sum(1 for trc in self if trc.isSelected)



# ==============================================================================
# Experiment Concrete Subclasses
# ==============================================================================
class FretExperiment(BaseExperiment):
    traceClass = traces.FretTrace
    classLabel = "fret"

class PiecewiseExperiment(BaseExperiment):
    traceClass = traces.PiecewiseTrace
    classLabel = "piecewise"

class PifeExperiment(BaseExperiment):
    traceClass = traces.PifeTrace
    classLabel = "pife"

class PifeCh2Experiment(BaseExperiment):
    traceClass = traces.PifeCh2Trace
    classLabel = "pife2"

class MultimerExperiment(BaseExperiment):
    traceClass = traces.MultimerTrace
    classLabel = "multimer"



# ==============================================================================
# EXPERIMENT FACTORY CLASS
# ==============================================================================
class Experiment():

    CLASS_TYPES = {"fret": FretExperiment,
                   "piecewise": PiecewiseExperiment,
                   "pife": PifeExperiment,
                   "pife2": PifeCh2Experiment,
                   "multimer": MultimerExperiment}

    @staticmethod
    def build(cls, D0, A0, S0, SP, pks, recordTime, frameLength,
                          info, img, bleed, gamma, comments=""):

        movID = SMTraceID.from_datetime(recordTime)
        movies = SMMovieList()
        movies.append(movID, img, info)

        traces = [cls.traceClass(movID.new_trace(j), np.vstack((d, a, s0, sp)),
                                 frameLength, pk=pk, bleed=bleed, gamma=gamma)
                  for j, (d, a, s0, sp, pk) in enumerate(zip(D0, A0, S0, SP, pks))]
        return cls(movies, traces, frameLength, comments)

    @staticmethod
    def from_pma(filename, experimentType, bleed=0.05, gamma=1, comments=""):
        filename = Path(filename)
        data = io.pma.read(filename.absolute())
        cls = Experiment.CLASS_TYPES[experimentType.lower()]
        return Experiment.build(cls, bleed=bleed, gamma=gamma, comments=comments, **data)

    @staticmethod
    def write_to_hdf(filename, experiment):
        filename = Path(filename).absolute()
        print(filename)
        print(type(filename))


        # def save(self, savename):
        # savename = os.path.abspath(savename)
        # with h5py.File(savename, "w") as HF:
        #     HF.attrs["experimentType"] = self.classLabel
        #     HF.attrs["frameLength"] = self.frameLength
        #     HF.attrs["comments"] = self.comments
        #     self._movies.to_hdf(HF)
        #     traceGroup = HF.create_group("traces")
        #     for trc in self:
        #         trc.to_hdf(traceGroup)
        #     # following attributes can be used for display in file manager
        #     HF.attrs["nTraces"] = len(self)
        #     HF.attrs["nSelected"] = self.nSelected
        #     HF.attrs["dateModified"] = datetime.now().strftime("%a %b %d, %Y\t%H:%M:%S")
        #     HF.attrs["version"] = smtirf.__version__
