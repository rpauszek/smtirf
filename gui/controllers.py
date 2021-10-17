from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal
from typing import ClassVar
from pathlib import Path

from .. import Experiment

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

    def __post_init__(self):
        super().__init__()

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

    def import_pma_file(self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""):
        self.experiment = Experiment.from_pma(filename, experimentType, bleed, gamma, comments)
        self.filename = Path(filename).with_suffix(".smtrc")

    def open_experiment(self, filename):
        self.experiment = Experiment.load(filename)
        self.filename = Path(filename)

    def save_experiment(self, filename):
        self.experiment.save(filename)
        self.filename = Path(filename)

    def select_all(self):
        self.experiment.select_all()
        self.traceStateChanged.emit(self.trace)

    def select_none(self):
        self.experiment.select_none()
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
