from dataclasses import dataclass
from PyQt5.QtCore import QObject
import pathlib

from .. import Experiment

@dataclass
class ExperimentController(QObject):
    filename: str = ""
    experiment: object = None
    trace: object = None
    index: int = 0

    def import_pma_file(self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""):
        self.experiment = Experiment.from_pma(filename, experimentType, bleed, gamma, comments)
        print(self.experiment)
