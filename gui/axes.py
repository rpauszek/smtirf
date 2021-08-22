from dataclasses import dataclass, InitVar
from typing import ClassVar
from matplotlib.axes import Axes

__all__ = ["TraceAxes"]


class BaseTraceDataAxes(Axes):

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        parent.traceChanged.connect(self.update_data)

    def update_data(self, trace):
        raise NotImplemented("base axes class cannot be instantiated")


class SelectedDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)
        self.lineFull, = self.plot([], [], color="k", lw=0.5)
        self.set_xmargin(0)
        self.set_ylim(-0.2, 1.2)

    def update_data(self, trace):
        self.lineFull.set_data(trace.t, trace.X)

        self.relim()
        self.autoscale(enable=True, axis="x")


class ChannelDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)

    def update_data(self, trace):
        pass


class TotalDataAxes(BaseTraceDataAxes):

    def __init__(self, *args, parent=None):
        super().__init__(*args, parent=parent)

    def update_data(self, trace):
        pass


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
