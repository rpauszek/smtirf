import numpy as np
from dataclasses import dataclass, InitVar
from typing import ClassVar
from matplotlib.axes import Axes

from . import config

__all__ = ["TraceAxes"]


class BaseTraceDataAxes(Axes):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.selectedSpan = self.axvspan(0, 1, **config.spans.selection)
        self.set_facecolor(config.colors.dim_background)
        self.axhline(0, color="k", lw="0.5")

        selected_span_updater = lambda trace: set_span_xlimits(self.selectedSpan,
                                                               trace.t[trace.limits][0],
                                                               trace.t[trace.limits][-1])

        parent.traceChanged.connect(selected_span_updater)
        parent.traceChanged.connect(self.update_data)

    def update_data(self, trace, relim):
        raise NotImplemented("base axes class cannot be instantiated")

    def make_line(self, color, **kwargs):
        formatting = {"lw": config.linewidths.default, **kwargs}
        line, = self.plot([], [], color=color, **formatting)
        return line


def relim(axis):
    def update(func):
        def wrapped_update(self, trace, relim):
            func(self, trace, relim)
            if relim:
                self.relim()
                self.autoscale(enable=True, axis=axis)
        return wrapped_update
    return update


class SelectedDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineFull = self.make_line(color=config.colors.selected_dim)
        self.lineSelected = self.make_line(color=config.colors.selected)
        self.lineFit = self.make_line(color=config.colors.fit, lw=config.linewidths.fit)
        self.set_xmargin(0)
        self.set_ylim(-0.2, 1.2)

    @relim("x")
    def update_data(self, trace, relim):
        self.lineFull.set_data(trace.t, trace.E)
        self.lineSelected.set_data(trace.t[trace.limits], trace.X)
        fit_data = (trace.t[trace.limits], trace.EP) if trace.model else ([], [])
        self.lineFit.set_data(*fit_data)


class ChannelDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineDonor = self.make_line(color=config.colors.donor)
        self.lineAcceptor = self.make_line(color=config.colors.acceptor)

        self.set_xmargin(0)
        self.set_ymargin(0.1)

    @relim("both")
    def update_data(self, trace, relim):
        self.lineDonor.set_data(trace.t, trace.D)
        self.lineAcceptor.set_data(trace.t, trace.A)


class TotalDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineFull = self.make_line(color=config.colors.total)

        self.set_xmargin(0)
        self.set_ymargin(0.1)

    @relim("both")
    def update_data(self, trace, relim):
        self.lineFull.set_data(trace.t, trace.I)


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


def set_span_xlimits(span, xmin, xmax):
    xy = span.get_xy()
    xy[[0, 1, 4], 0] = xmin
    xy[[2, 3], 0] = xmax
    span.set_xy(xy)
