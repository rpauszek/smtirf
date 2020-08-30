# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> __init__
"""
import numpy as np
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

from .. import CONFIG

# ==============================================================================
# base canvas classes
# ==============================================================================
class QtCanvas(FigureCanvas):

    def __init__(self, controller):
        self.controller = controller
        self.fig = Figure()
        super().__init__(self.fig)

        bgcolor = QtWidgets.QWidget().palette().color(QtGui.QPalette.Background)
        self.fig.set_facecolor(np.array(bgcolor.getRgb()[:-1])/255)

        self.fig.set_tight_layout(True)
        self.layout()
        self.fig.align_labels()
        self.connect()

    def layout(self):
        pass

    def connect(self):
        pass


class ScrollableCanvas(QtCanvas):

    def connect(self):
        self.mpl_connect("scroll_event", self._trigger_scroll)

    def _trigger_scroll(self, evt):
        self.controller.stepIndexTriggered.emit(evt.step)

# ==============================================================================
# Interactive axes "interfaces"
# ==============================================================================
class InteractiveCanvas():

    def set_zoom_axes(self, ax, button=1):
        rectProps = {"alpha": 0.5, "facecolor": CONFIG.colors["span"]["zoom"]}
        spanArgs = {"useblit": True, "button": button, "rectprops": rectProps}
        self.zoomSpan = SpanSelector(ax, self.on_zoom, 'horizontal', **spanArgs)

    def set_baseline_axes(self, ax, button=3):
        rectProps = {"alpha": 0.5, "facecolor": CONFIG.colors["span"]["offset"]} 
        spanArgs = {"useblit": True, "button": button, "rectprops": rectProps, "minspan": 0.5}
        self.baselineSpan = SpanSelector(ax, self.controller.set_trace_offset_time_window,
                                         'horizontal', **spanArgs)

    # def set_blink_axes(self, ax, button=1):
    #     rectProps = {"alpha": 0.5, "facecolor": "#D30000"}
    #     spanArgs = {"useblit": True, "button": button, "rectprops": rectProps}
    #     self.blinkSpan = SpanSelector(ax, self.controller.set_blink_time_window,
    #                                      'horizontal', **spanArgs)

    def on_zoom(self, xmin, xmax):
        if xmax-xmin > 1:
            for ax in self.fig.axes:
                ax.set_xlim(xmin, xmax)
            self.draw()




from . import axes_trace
from .canvases_traceviewer import *
