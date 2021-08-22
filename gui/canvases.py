import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from .axes import TraceAxes


# ==============================================================================
# base canvas classes
# ==============================================================================
class QtCanvas(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)
        bgcolor = QtWidgets.QWidget().palette().color(QPalette.Background)
        self.fig.set_facecolor(np.array(bgcolor.getRgb()[:-1])/255)
        self.fig.set_tight_layout(True)


class InteractiveTraceViewer(QtCanvas):

    traceChanged = pyqtSignal(object)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        gs = self.fig.add_gridspec(3, 1)
        self.axSelection = self.fig.add_subplot(gs[0], projection=TraceAxes(parent=self, dataType="selection"))
        self.axChannels = self.fig.add_subplot(gs[1], projection=TraceAxes(parent=self, dataType="channels"))
        self.axTotal = self.fig.add_subplot(gs[2], projection=TraceAxes(parent=self, dataType="total"))

        controller.traceChanged.connect(self.update_plots)

    def update_plots(self, trace):
        self.traceChanged.emit(trace)
        self.draw()
