import numpy as np
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal
from typing import ClassVar
from pathlib import Path

from .. import Experiment
from . import threads, dialogs


@dataclass
class ExperimentController(QObject):
    filename: str = ""
    _experiment: object = None
    _trace: object = None
    _index: int = 0
    experimentChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    traceIndexChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    traceStateChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    stepIndexTriggered: ClassVar[pyqtSignal] = pyqtSignal(int)
    mplMotionNotifyEvent: ClassVar[pyqtSignal] = pyqtSignal(object)
    trainingStarted: ClassVar[pyqtSignal] = pyqtSignal()
    trainingFinished: ClassVar[pyqtSignal] = pyqtSignal(object)

    def __post_init__(self):
        super().__init__()
        self.training_thread = threads.TrainGlobalThread(self)
        self.training_thread.started_training.connect(self.trainingStarted.emit)
        self.training_thread.finished_training.connect(
            lambda: self.trainingFinished.emit(self._get_model())
        )

    def _get_model(self):
        for trace in self.experiment:
            if trace.isSelected:
                return trace.model

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, value):
        self._experiment = value
        self.experimentChanged.emit(self.experiment)

    @property
    def trace(self):
        return self._trace

    @property
    def index(self):
        return self._index

    def set_index(self, value):
        self._index = value
        self.set_trace(self.index)

    def set_trace(self, index):
        self._trace = self.experiment[index]
        self.traceIndexChanged.emit(self.trace)

    def import_pma_file(
        self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""
    ):
        self.experiment = Experiment.from_pma(
            filename, experimentType, bleed, gamma, comments
        )
        self.filename = Path(filename).with_suffix(".smtrc")

    def open_experiment(self, filename):
        self.experiment = Experiment.load(filename)
        self.filename = Path(filename)

    def save_experiment(self, filename):
        self.experiment.save(filename)
        self.filename = Path(filename)

    def sort_traces(self, method):
        self.experiment.sort(method)
        self.set_index(self.index)

    def select_all(self):
        self.experiment.select_all()
        self.traceStateChanged.emit(self.trace)

    def select_none(self):
        self.experiment.select_none()
        self.traceStateChanged.emit(self.trace)

    def reset_limits(self):
        for trace in self.experiment:
            trace.set_limits(None)
        self.traceStateChanged.emit(self.trace)

    def reset_offsets(self):
        for trace in self.experiment:
            trace.set_offsets(None)
        self.traceStateChanged.emit(self.trace)

    def reset_trace(self):
        self.trace.set_limits(None)
        self.trace.set_offsets(None)
        self.traceStateChanged.emit(self.trace)

    def set_trace_offset_time_window(self, tmin, tmax):
        self.trace.set_offset_time_window(tmin, tmax)
        self.traceStateChanged.emit(self.trace)

    def set_trace_start_time(self, time):
        self.trace.set_start_time(time)
        self.traceStateChanged.emit(self.trace)

    def set_trace_stop_time(self, time):
        self.trace.set_stop_time(time)
        self.traceStateChanged.emit(self.trace)

    def toggle_selected(self):
        self.trace.toggle()
        self.traceStateChanged.emit(self.trace)

    def train_global(self, nstates, shared_var):
        self.training_thread.set_parameters(nstates, shared_var)
        self.training_thread.start()

    def remove_problem_traces(self):
        for trace in self.experiment:
            if trace.isSelected:
                if np.logical_or(np.any(trace.X < -0.5), np.any(trace.X > 1.5)):
                    trace.isSelected = False
        self.traceStateChanged.emit(self.trace)

    def show_results(self, kind):
        match kind:
            case "hist":
                dlg = dialogs.SplitHistogramDialog(self.experiment)
            case "tdp":
                dlg = dialogs.TdpDialog(self.experiment)
            case "dwell":
                raise NotImplementedError("Dwelltime analysis is not yet implemented.")
            case _:
                raise ValueError(f"'kind' argument '{kind}' not valid.")

        _ = dlg.exec()


@dataclass
class ModelController(QObject):
    _nstates: int = 2
    _shared_var: bool = False
    numberOfStatesChanged: ClassVar[pyqtSignal] = pyqtSignal(int)
    sharedVarChanged: ClassVar[pyqtSignal] = pyqtSignal(bool)
    trainGlobalModel: ClassVar[pyqtSignal] = pyqtSignal(int, bool)
    updateExitFlag: ClassVar[pyqtSignal] = pyqtSignal(object)

    def __post_init__(self):
        super().__init__()

    def set_nstates(self, value):
        self._nstates = value

    def set_shared_var(self, value):
        self._shared_var = value

    def call_train_global(self):
        self.trainGlobalModel.emit(self._nstates, self._shared_var)
