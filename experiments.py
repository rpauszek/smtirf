# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> experiments
"""
from . import traces

# ==============================================================================
# BASE EXPERIMENT CLASS
# ==============================================================================
class BaseExperiment():

    def __init__(self, movies, traces, frameLength, comments=""):
        self._movies = movies
        self._traces = traces
        self.frameLength = frameLength
        self.comments = comments

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
