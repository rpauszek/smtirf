from dataclasses import dataclass
from PyQt5.QtCore import QObject
from pathlib import Path

from .. import Experiment

@dataclass
class ExperimentController(QObject):
    filename: str = ""
    experiment: object = None
    trace: object = None
    index: int = 0

    def import_pma_file(self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""):
        self.experiment = Experiment.from_pma(filename, experimentType, bleed, gamma, comments)
        self.filename = Path(filename).with_suffix(".smtrc")
        print(self.experiment)

    def save_experiment(self, filename):
        self.experiment.save(filename)
        self.filename = Path(filename)
        print(filename)
