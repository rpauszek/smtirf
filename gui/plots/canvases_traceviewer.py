# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> canvases_traceviewer
"""
from matplotlib.gridspec import GridSpec
import matplotlib as mpl

from . import QtCanvas, ScrollableCanvas, InteractiveCanvas

__all__ = ["TraceViewerPlot"]

class TraceViewerPlot(ScrollableCanvas, InteractiveCanvas):

    def connect(self):
        super().connect()
        self.controller.currentTraceChanged.connect(self.update_plots)
        self.controller.traceEdited.connect(self.update_plots)
        self.controller.selectedEdited.connect(self.update_plots)
        self.controller.modelTrained.connect(self.update_plots)
        self.mpl_connect('motion_notify_event', self.controller.motion_notify)
        self.mpl_connect('button_release_event', self.on_release)
        self.controller.experimentLoaded.connect(self.refresh)

    def refresh(self, expt):
        for ax in self.fig.axes:
            ax.remove()
        gs = GridSpec(3, 1)
        self.ax1 = self.fig.add_subplot(gs[0], projection=expt.classLabel)
        self.ax2 = self.fig.add_subplot(gs[1], projection="donoracceptor")
        self.ax3 = self.fig.add_subplot(gs[2], projection="total")

        self.set_zoom_axes(self.ax1, button=1)
        self.set_baseline_axes(self.ax3, button=3)
        self.draw()

    def update_plots(self, trc):
        for ax in self.fig.axes:
            try:
                ax.set_trace(trc)
            except AttributeError:
                # thrown when Experiment type changes, because ref still active
                # til garbage collected
                pass
        self.draw()

    def on_release(self, evt):
        if evt.inaxes == self.ax2 and evt.xdata is not None:
            if evt.button == 1: # start
                self.controller.set_trace_start_time(evt.xdata)
            elif evt.button == 3: # stop
                self.controller.set_trace_stop_time(evt.xdata)
        elif evt.inaxes == self.ax1 and evt.button == 3:
            for ax in self.fig.axes:
                ax.unzoom()
            self.draw()
