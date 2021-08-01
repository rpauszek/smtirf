from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal
from typing import ClassVar
from pathlib import Path

from .. import Experiment

@dataclass
class ExperimentController(QObject):
    filename: str = ""
    _experiment: object = None
    trace: object = None
    index: int = 0
    experimentChanged: ClassVar[pyqtSignal] = pyqtSignal()

    def __post_init__(self):
        super().__init__()

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, val):
        self._experiment = val
        self.experimentChanged.emit()
        print("exeriment set")

    def import_pma_file(self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""):
        self.experiment = Experiment.from_pma(filename, experimentType, bleed, gamma, comments)
        self.filename = Path(filename).with_suffix(".smtrc")
        print(self.experiment)

    def open_experiment(self, filename):
        self.experiment = Experiment.load(filename)
        self.filename = Path(filename)
        print(self._experiment, "*")
        print(self.experiment)

    def save_experiment(self, filename):
        self.experiment.save(filename)
        self.filename = Path(filename)
        print(filename)
