# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> axes_results
"""
import numpy as np

from matplotlib.widgets import Cursor
import matplotlib.ticker as ticker
import matplotlib as mpl

from ..dialogs import NoResultsMessageBox
from .. import CONFIG

class ResultAxes(mpl.axes.Axes):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.axhline(0, c='k', lw=0.5)

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

    def unzoom(self):
        self.relim()
        self.autoscale(enable=True, axis="both")


class SplitHistAxes(ResultAxes):
    name = "splithist"
    YLABEL = "counts"
    XLABEL = "SIGNAL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.margins(x=0, y=0.05)

    def update_view(self, expt):
        h = expt.results.hist
        # try:
        self.cla()
        self.step(h.centers, h.total, where="mid", c="k")
        for state, population in zip(h.states, h.populations):
            lbl = f"{population*100:0.2f}%"
            self.bar(h.centers, state, width=h.width, alpha=0.75, label=lbl)
        self.legend()
        # except TypeError:
        #     msg = NoResultsMessageBox()
        #     msg.exec_()

        # matplotlib.pyplot.bar(x, height, width=0.8, bottom=None, *, align='center'

    # def set_trace(self, trc):
    #     key = "selected" if trc.isSelected else "active"
    #     self._lineD.set_data(trc.t, trc.D)
    #     self._lineD.set_color(CONFIG.colors["donor"][key])
    #     self._lineA.set_data(trc.t, trc.A)
    #     self._lineA.set_color(CONFIG.colors["acceptor"][key])

    #     self.relim()
    #     self.autoscale(enable=True, axis="both")   


class TdpAxes(ResultAxes):
    name = "tdp"
    YLABEL = "Final"
    XLABEL = "Initial"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

    def update_view(self, expt):
        t = expt.results.tdp
        self.cla()
        self.contourf(t.X, t.Y, t.Z, 150, cmap='jet')


class KineticsAxes(ResultAxes):
    name = "kinetics"
    YLABEL = "counts"
    XLABEL = "dwell time"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)           

    def update_view(self, expt):
        print("*", expt)


mpl.projections.register_projection(SplitHistAxes)
mpl.projections.register_projection(TdpAxes)
mpl.projections.register_projection(KineticsAxes)