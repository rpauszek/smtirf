# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> canvases_results
"""
from matplotlib.gridspec import GridSpec
import matplotlib as mpl

from . import QtCanvas, ScrollableCanvas, InteractiveCanvas

__all__ = ["ResultViewerPlot"]

class ResultViewerPlot(QtCanvas):

    def connect(self):
        super().connect()
        # self.controller.currentTraceChanged.connect(self.update_plots)
        # self.controller.traceEdited.connect(self.update_plots)
        # self.controller.selectedEdited.connect(self.update_plots)
        # self.controller.modelTrained.connect(self.update_plots)
        # self.mpl_connect('motion_notify_event', self.controller.motion_notify)
        # self.mpl_connect('button_release_event', self.on_release)
        # self.controller.experimentLoaded.connect(self.refresh)
        self.controller.currentResultViewChanged.connect(self.change_view)

    def change_view(self, view):
        gs = GridSpec(1, 1)
        for ax in self.fig.axes:
            self.ax.remove()
        self.ax = self.fig.add_subplot(gs[0], projection=view)
        self.draw()
