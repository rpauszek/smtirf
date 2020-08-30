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
        self._lineInactive, = self.plot([], [], CONFIG.colors["fret"]["inactive"])
        self._lineActive, = self.plot([], [], CONFIG.colors["fret"]["active"])
        self._lineFit, = self.plot([], [], CONFIG.colors["fret"]["fit"], lw=2)

        self.margins(x=0)
        self.set_ylim(*CONFIG.opts["fretLims"])

    def set_trace(self, trc):
        key = "selected" if trc.isSelected else "active"
        self._lineInactive.set_data(trc.t, trc.E)
        self._lineActive.set_data(trc.t[trc.limits], trc.X)
        self._lineActive.set_color(CONFIG.colors["fret"][key])
        if trc.model is not None:
            self._lineFit.set_data(trc.t[trc.limits], trc.EP)
        else:
            self._lineFit.set_data([], [])

        self.relim()
        self.autoscale(enable=True, axis="x")


class DonorAcceptorAxes(TraceAxes):
    name = "donoracceptor"
    YLABEL = "D/A signal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lineD, = self.plot([], [], CONFIG.colors["donor"]["active"])
        self._lineA, = self.plot([], [], CONFIG.colors["acceptor"]["active"])

        self.margins(x=0, y=0.05)

    def set_trace(self, trc):
        key = "selected" if trc.isSelected else "active"
        self._lineD.set_data(trc.t, trc.D)
        self._lineD.set_color(CONFIG.colors["donor"][key])
        self._lineA.set_data(trc.t, trc.A)
        self._lineA.set_color(CONFIG.colors["acceptor"][key])

        self.relim()
        self.autoscale(enable=True, axis="both")


class TotalIntensityAxes(TraceAxes):
    name = "total"
    YLABEL = "Total signal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lineInactive, = self.plot([], [], CONFIG.colors["total"]["background"])
        self._lineActive, = self.plot([], [], CONFIG.colors["total"]["active"])

        self.margins(x=0, y=0.05)

    def set_trace(self, trc):
        key = "selected" if trc.isSelected else "active"
        self._lineInactive.set_data(trc.t, trc.I)
        Isig = trc.I.copy()
        Isig[trc.S0 != 0] = np.nan
        self._lineActive.set_data(trc.t, Isig)
        self._lineActive.set_color(CONFIG.colors["total"][key])


        self.relim()
        self.autoscale(enable=True, axis="both")


mpl.projections.register_projection(FretAxes)
mpl.projections.register_projection(DonorAcceptorAxes)
mpl.projections.register_projection(TotalIntensityAxes)