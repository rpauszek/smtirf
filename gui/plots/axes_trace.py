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

class TraceAxes(mpl.axes.Axes):
    XLABEL = "Time (sec)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.axhline(0, c='k', lw=0.5)
        
        if self.is_first_col():
            self.show_ylabel()
        else:
            self.hide_ylabel()

        if self.is_last_row():
            self.show_xlabel()
        else:
            self.hide_xlabel()

    def show_xlabel(self):
        self.set_xlabel(self.XLABEL)

    def hide_xlabel(self):
        self.set_xlabel("")
        self.set_xticklabels("")

    def show_ylabel(self):
        self.set_ylabel(self.YLABEL)

    def hide_ylabel(self):
        self.set_ylabel("")
        self.set_yticklabels("")


class FretAxes(TraceAxes):
    name = "fret"
    YLABEL = "FRET"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.margins(x=0)
        self.set_ylim(*CONFIG.opts["fretLims"])

    def set_trace(self, trc):
        self.relim()
        self.autoscale(enable=True, axis="x")


class DonorAcceptorAxes(TraceAxes):
    name = "donoracceptor"
    YLABEL = "D/A signal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.margins(x=0, y=0.05)

    def set_trace(self, trc):
        self.relim()
        self.autoscale(enable=True, axis="both")


class TotalIntensityAxes(TraceAxes):
    name = "total"
    YLABEL = "Total signal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.margins(x=0, y=0.05)

    def set_trace(self, trc):
        self.relim()
        self.autoscale(enable=True, axis="both")


mpl.projections.register_projection(FretAxes)
mpl.projections.register_projection(DonorAcceptorAxes)
mpl.projections.register_projection(TotalIntensityAxes)
