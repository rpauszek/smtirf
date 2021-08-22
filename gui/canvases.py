import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

from . import config
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
        self.mpl_connect("scroll_event", lambda evt: controller.stepIndexTriggered.emit(evt.step))

    def make_axes(self):
        for j, (dataType, ax) in enumerate(self.axes.items()):
            if ax is not None:
                ax.remove()
            projection = TraceAxes(parent=self, dataType=dataType)
            self.axes[dataType] = self.figure.add_subplot(self.gs[j], projection=projection)
        self.make_span_selectors()

    def make_span_selectors(self):
        def on_zoom(xmin, xmax):
            if xmax-xmin < 1:
                return
            for _, ax in self.axes.items():
                ax.set_xlim(xmin, xmax)
            self.draw()

        self.zoomSpan = SpanSelector(self.axes["selection"], on_zoom, "horizontal",
                                     useblit=True, button=1, rectprops=config.plot.zoom_span)

    def update_plots(self, trace):
        self.traceChanged.emit(trace)
        self.draw()
