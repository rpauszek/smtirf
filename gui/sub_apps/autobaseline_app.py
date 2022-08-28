from dataclasses import dataclass
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

from .. import widgets
from ..canvases import QtCanvas
from ...src.util.autobaseline import AutoBaselineModel


class AutobaselineApp(QtWidgets.QWidget):
    def __init__(self, experiment):
        super().__init__(windowTitle="Automated Baseline Estimation")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.controller = AutobaselineController(experiment)
        self.layout()

        self.show()

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(AutobaselineParametersGroup(self.controller))
        hbox.addWidget(BaselineGmmCanvas(self.controller), stretch=1)

        vbox.addLayout(hbox, stretch=1)
        vbox.addWidget(BaselineTraceCanvas(self.controller), stretch=1)


class AutobaselineParametersGroup(QtWidgets.QGroupBox):
    def __init__(self, controller):
        super().__init__("Detection Parameters")
        self.controller = controller
        self.layout()

    def layout(self):
        box = QtWidgets.QVBoxLayout()

        # Paramter widgets
        w = widgets.LabeledSlider(
            "GMM components",
            minimum=2,
            maximum=10,
            value=self.controller.gmm_components,
        )
        w.valueChanged.connect(
            lambda val: setattr(self.controller, "gmm_components", val)
        )
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider(
            "GMM sample size",
            minimum=1e3,
            maximum=1e5,
            value=self.controller.gmm_sample_size,
            interval=1e3,
        )
        w.valueChanged.connect(
            lambda val: setattr(self.controller, "gmm_sample_size", val)
        )
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider(
            "GMM maximum iterations",
            minimum=25,
            maximum=1500,
            value=self.controller.gmm_iterations,
            interval=25,
        )
        w.valueChanged.connect(
            lambda val: setattr(self.controller, "gmm_iterations", val)
        )
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledScientificSlider(
            "GMM convergence tolerance",
            minimum=1e-12,
            maximum=1,
            value=self.controller.gmm_tol,
        )
        w.valueChanged.connect(lambda val: setattr(self.controller, "gmm_tol", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider(
            "HMM maximum iterations",
            minimum=25,
            maximum=1500,
            value=self.controller.hmm_iterations,
            interval=25,
        )
        w.valueChanged.connect(
            lambda val: setattr(self.controller, "hmm_iterations", val)
        )
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledScientificSlider(
            "HMM convergence tolerance",
            minimum=1e-12,
            maximum=1,
            value=self.controller.hmm_tol,
        )
        w.valueChanged.connect(lambda val: setattr(self.controller, "hmm_tol", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Expanding))

        # Buttons
        hbox = QtWidgets.QHBoxLayout()
        w = QtWidgets.QPushButton("Train GMM")
        w.clicked.connect(self.controller.train_gmm)
        self.controller.gmmTrainingThread.trainingStarted.connect(lambda: w.setEnabled(False))
        self.controller.gmmTrainingThread.trainingFinished.connect(lambda: w.setEnabled(True))
        hbox.addWidget(w)

        w = QtWidgets.QPushButton("Train HMM")
        w.setEnabled(False)
        w.clicked.connect(self.controller.train_hmm)
        self.controller.gmmTrainingThread.trainingFinished.connect(lambda: w.setEnabled(True))
        self.controller.hmmTrainingThread.trainingStarted.connect(lambda: w.setEnabled(False))
        self.controller.hmmTrainingThread.trainingFinished.connect(lambda: w.setEnabled(True))

        hbox.addWidget(w)

        box.addLayout(hbox)
        self.setLayout(box)


class BaselineGmmCanvas(QtCanvas):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)
        # self.controller.gmmTrainingThread.trainingStarted.connect()


class BaselineTraceCanvas(QtCanvas):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)


class BaselineTrainingThread(QtCore.QThread):

    trainingStarted = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, controller, kind):
        super().__init__()
        self.controller = controller
        self.kind = kind

    def __del__(self):
        self.wait()

    def run(self):
        self.trainingStarted.emit()
        if self.kind == "gmm":
            self.controller.model.train_gmm(
                nComponents=self.controller.gmm_components,
                nPoints=self.controller.gmm_sample_size,
            )
        if self.kind == "hmm":
            self.controller.model.train_hmm(
                maxIter=self.controller.hmm_iterations,
                tol=self.controller.hmm_tol,
            )
        self.trainingFinished.emit()


@dataclass
class AutobaselineController(QtCore.QObject):
    experiment: object
    gmm_components: int = 2
    gmm_sample_size: int = 1e4
    gmm_iterations: int = 250
    gmm_tol: float = 1e-3
    hmm_iterations: int = 250
    hmm_tol: float = 1e-3

    def __post_init__(self):
        super().__init__()
        self.gmmTrainingThread = BaselineTrainingThread(self, "gmm")
        self.hmmTrainingThread = BaselineTrainingThread(self, "hmm")
        self.model = AutoBaselineModel(self.experiment)

    def train_gmm(self):
        self.gmmTrainingThread.start()

    def train_hmm(self):
        self.hmmTrainingThread.start()
