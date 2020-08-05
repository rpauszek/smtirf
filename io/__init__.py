# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> io >> __init__
"""
import numpy as np
from pathlib import Path
from . import pma
from .. import SMTraceID, SMMovieList
from .. import experiments, traces

# ==============================================================================
# EXPERIMENT FACTORY CLASS
# ==============================================================================
class Experiment():

    CLASS_TYPES = {"fret": experiments.FretExperiment,
                   "piecewise": experiments.PiecewiseExperiment,
                   "pife": experiments.PifeExperiment,
                   "pife2": experiments.PifeCh2Experiment,
                   "multimer": experiments.MultimerExperiment}

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
        data = pma.read(filename.absolute())
        cls = Experiment.CLASS_TYPES[experimentType.lower()]
        return Experiment.build(cls, bleed=bleed, gamma=gamma, comments=comments, **data)
