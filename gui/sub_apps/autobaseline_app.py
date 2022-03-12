from dataclasses import dataclass
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

from .. import widgets
from ..canvases import QtCanvas


class AutobaselineApp(QtWidgets.QWidget):

    def __init__(self):
        super().__init__(windowTitle="Automated Baseline Estimation")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.controller = AutobaselineController()
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
        w = widgets.LabeledSlider("GMM components", minimum=2, maximum=10, value=self.controller.gmm_components)
        w.valueChanged.connect(lambda val: setattr(self.controller, "gmm_components", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider("GMM sample size", minimum=1e3, maximum=1e5, value=self.controller.gmm_sample_size, interval=1e3)
        w.valueChanged.connect(lambda val: setattr(self.controller, "gmm_sample_size", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider("GMM maximum iterations", minimum=25, maximum=1500, value=self.controller.gmm_iterations, interval=25)
        w.valueChanged.connect(lambda val: setattr(self.controller, "gmm_iterations", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledScientificSlider("GMM convergence tolerance", minimum=1e-12, maximum=1, value=self.controller.gmm_tol)
        w.valueChanged.connect(lambda val: setattr(self.controller, "gmm_tol", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledIntervalSlider("HMM maximum iterations", minimum=25, maximum=1500, value=self.controller.hmm_iterations, interval=25)
        w.valueChanged.connect(lambda val: setattr(self.controller, "hmm_iterations", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))

        w = widgets.LabeledScientificSlider("HMM convergence tolerance", minimum=1e-12, maximum=1, value=self.controller.hmm_tol)
        w.valueChanged.connect(lambda val: setattr(self.controller, "hmm_tol", val))
        box.addWidget(w)
        box.addItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Expanding))

        # Buttons
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QPushButton("Train GMM"))
        hbox.addWidget(QtWidgets.QPushButton("Train HMM"))
        box.addLayout(hbox)

        self.setLayout(box)


class BaselineGmmCanvas(QtCanvas):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)


class BaselineTraceCanvas(QtCanvas):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)


@dataclass
class AutobaselineController(QtCore.QObject):
    gmm_components: int = 2
    gmm_sample_size: int = 1e4
    gmm_iterations: int = 250
    gmm_tol: float = 1e-3
    hmm_iterations: int = 250
    hmm_tol: float = 1e-3

    def __init__(self):
        pass
    def __post_init__(self):
        super().__init__()