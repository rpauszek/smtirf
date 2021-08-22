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
        self.figure = Figure()
        super().__init__(self.figure)
        bgcolor = QtWidgets.QWidget().palette().color(QPalette.Background)
        self.figure.set_facecolor(np.array(bgcolor.getRgb()[:-1])/255)
        self.figure.set_tight_layout(True)


class InteractiveTraceViewer(QtCanvas):

    traceChanged = pyqtSignal(object)
    axes = {"selection": None,
            "channels": None,
            "total": None}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.gs = self.figure.add_gridspec(3, 1)

        controller.experimentChanged.connect(self.make_axes)
        controller.traceChanged.connect(self.update_plots)

    def make_axes(self):
        for j, (dataType, ax) in enumerate(self.axes.items()):
            if ax is not None:
                ax.remove()
            projection = TraceAxes(parent=self, dataType=dataType)
            ax = self.figure.add_subplot(self.gs[j], projection=projection)

    def update_plots(self, trace):
        self.traceChanged.emit(trace)
        self.draw()
