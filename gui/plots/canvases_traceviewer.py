# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> canvases_traceviewer
"""
from matplotlib.widgets import SpanSelector
from matplotlib.gridspec import GridSpec
import matplotlib as mpl

from . import QtCanvas, ScrollableCanvas

__all__ = ["FretExperimentViewerPlot"]

class BaseTraceViewerPlot(ScrollableCanvas):

    def connect(self):
        super().connect()
    #     self.controller.currentTraceChanged.connect(self.update_plots)
    #     self.controller.traceEdited.connect(self.update_plots)
    #     self.controller.selectedEdited.connect(self.update_plots)
    #     self.mpl_connect('motion_notify_event', self.controller.motion_notify)
    #     self.mpl_connect('button_release_event', self.on_release)
    #
    # def update_plots(self, trc):
    #     for ax in self.fig.axes:
    #         ax.set_trace(trc)
    #     self.draw()

class FretExperimentViewerPlot(BaseTraceViewerPlot):

    def __init__(self, controller):
        super().__init__(controller)
        # self.set_zoom_axes(self.axE, button=1)
        # self.set_baseline_axes(self.axI, button=3)

    def layout(self):
        gs = GridSpec(3, 1)
        self.axE = self.fig.add_subplot(gs[0], projection="fret")
        self.axDA = self.fig.add_subplot(gs[1], projection="donoracceptor")
        self.axI = self.fig.add_subplot(gs[2], projection="total")
