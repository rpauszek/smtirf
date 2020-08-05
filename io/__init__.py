# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> io >> __init__
"""
from pathlib import Path
from . import pma
from .. import experiments

# ==============================================================================
# EXPERIMENT FACTORY CLASS
# ==============================================================================
class Experiment():

    # CLASS_TYPES = {"fret": FretExperiment,
    #                "piecewise": PiecewiseExperiment,
    #                "pife": PifeExperiment,
    #                "pife2": PifeCh2Experiment,
    #                "multimer": MultimerExperiment}

    @staticmethod
    def build(cls, D0, A0, S0, SP, pks, recordTime, frameLength,
                          info, img, bleed, gamma):
        movies = smtirf.data.MovieList.from_movie(img, recordTime, info)
        movID = smtirf.SMTraceID.from_datetime(recordTime)
        traces = [cls.build_trace(movID.new_trace(j), np.vstack((d, a, s0, sp)),
                                  frameLength, pk=pk, bleed=bleed, gamma=gamma)
                  for j, (d, a, s0, sp, pk) in enumerate(zip(D0, A0, S0, SP, pks))]
        return cls(movies, traces, frameLength)

    @staticmethod
    def from_pma(filename):
        filename = Path(filename)
        data = pma.read(filename.absolute())
        print(data["frameLength"])
        # cls = Experiment.CLASS_TYPES[experimentType]
