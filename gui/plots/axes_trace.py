# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> axes_trace
"""
import numpy as np

from matplotlib.widgets import Cursor
import matplotlib.ticker as ticker
import matplotlib as mpl

from .. import CONFIG


class FretAxes(mpl.axes.Axes):
    name = "fret"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.axhline(0, c='k', lw=0.5)
        self.margins(x=0)
        self.set_ylabel("FRET")
        self.set_xlabel("Time (sec)")
        self.set_ylim(*CONFIG.opts["fretLims"])

    def set_trace(self, trc):
        self.relim()
        self.autoscale(enable=True, axis="x")

mpl.projections.register_projection(FretAxes)
