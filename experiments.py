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

    def __init__(self):
        pass

    @classmethod
    def build_trace(cls, trcID, data, frameLength, pk, bleed, gamma):
        pass




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
