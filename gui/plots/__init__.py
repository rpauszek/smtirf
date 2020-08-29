# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> plots >> __init__
"""
import numpy as np
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

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


from . import axes_trace
from .canvases_traceviewer import *
