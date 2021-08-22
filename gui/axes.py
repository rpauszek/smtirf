from dataclasses import dataclass, InitVar
from typing import ClassVar
from matplotlib.axes import Axes

from . import config

__all__ = ["TraceAxes"]


class BaseTraceDataAxes(Axes):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        parent.traceChanged.connect(self.update_data)

    def update_data(self, trace):
        raise NotImplemented("base axes class cannot be instantiated")

    def make_line(self, color):
        line, = self.plot([], [], color=color, lw=config.plot.line_width)
        return line


class SelectedDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineFull = self.make_line(color=config.plot.x_color)
        self.set_xmargin(0)
        self.set_ylim(-0.2, 1.2)

    def update_data(self, trace):
        self.lineFull.set_data(trace.t, trace.X)

        self.relim()
        self.autoscale(enable=True, axis="x")


class ChannelDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineDonor = self.make_line(color=config.plot.d_color)
        self.lineAcceptor = self.make_line(color=config.plot.a_color)
        self.set_xmargin(0)
        self.set_ymargin(0.1)

    def update_data(self, trace):
        self.lineDonor.set_data(trace.t, trace.D)
        self.lineAcceptor.set_data(trace.t, trace.A)

        self.relim()
        self.autoscale(enable=True, axis="both")


class TotalDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineFull = self.make_line(color=config.plot.i_color)
        self.set_xmargin(0)
        self.set_ymargin(0.1)

    def update_data(self, trace):
        self.lineFull.set_data(trace.t, trace.I)

        self.relim()
        self.autoscale(enable=True, axis="both")


@dataclass
class TraceAxes:
    parent: object
    dataType: InitVar[str]
    axesTypes: ClassVar[dict] = {"selection": SelectedDataAxes,
                                 "channels": ChannelDataAxes,
                                 "total": TotalDataAxes}

    def __post_init__(self, dataType):
        self.cls = TraceAxes.axesTypes[dataType]

    def _as_mpl_axes(self):
        return self.cls, {"parent": self.parent}
