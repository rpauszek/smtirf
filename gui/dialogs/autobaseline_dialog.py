# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> autobaseline_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets, plots, threads
from smtirf.gui.controllers import AutoBaselineController
import numpy as np

# TODO ==> clean up threading!! maybe new thread each time button is clicked?

class AutoBaselineDialog(QtWidgets.QDialog):

    filesUpdated = QtCore.pyqtSignal()

    def __init__(self, expt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = AutoBaselineController(expt)
        self.layout()
        self.connect()

        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))
        self.setWindowTitle("Auto-Detect Baseline")
        self.setMinimumWidth(650)

    def layout(self):
        gbox = QtWidgets.QGridLayout()
        gbox.setColumnStretch(1, 1)
        self.setLayout(gbox)

        gbox.addWidget(BaselineModelGroupBox(self.controller), 0, 0)
        gbox.addWidget(BaselineGmmCanvas(self.controller), 0, 1)
        gbox.addWidget(BaselineHmmCanvas(self), 1, 0, 1, 2)
        gbox.addWidget(widgets.NavBar(self.controller), 2, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        gbox.addWidget(self.buttonBox, 3, 0, 1, 2)

    def connect(self):
        self.controller.gmmTrainingThread.trainingStarted.connect(lambda: self.buttonBox.setEnabled(False))
        self.controller.gmmTrained.connect(lambda: self.buttonBox.setEnabled(True))


class BaselineModelGroupBox(QtWidgets.QGroupBox):

    def __init__(self, controller):
        super().__init__("Model Parameters")
        self.controller = controller
        self.layout()
        self.connect()

    def layout(self):
        self.spnGmmComponents = widgets.base.IntegerLineEdit(10, minimum=2, maximum=50)
        self.txtGmmNPoints = widgets.base.IntegerLineEdit(1e4, minimum=100, maximum=1e5)
        # self.spnGmmMaxIter = widgets.base.IntegerLineEdit(250, minimum=10, maximum=1e4)
        # self.txtGmmTol = widgets.base.ScientificLineEdit(1e-3, minimum=0, maximum=10)
        self.spnHmmMaxIter = widgets.base.IntegerLineEdit(250, minimum=10, maximum=1e4)
        self.txtHmmTol = widgets.base.ScientificLineEdit(1e-3, minimum=0, maximum=10)

        gbox = QtWidgets.QGridLayout()
        gbox.setColumnStretch(0, 1)
        self.setLayout(gbox)
        controls = (self.spnGmmComponents, self.txtGmmNPoints,
                    # self.spnGmmMaxIter, self.txtGmmTol,
                    self.spnHmmMaxIter, self.txtHmmTol)
        labels = ("GMM Components", "GMM Sample Size",
                  # "GMM Max Iterations", "GMM Tolerance",
                  "HMM Max Iterations", "HMM Tolerance")
        for row, (control, label) in enumerate(zip(controls, labels)):
            control.setMaximumWidth(60)
            gbox.addWidget(QtWidgets.QLabel(label+": "), row, 0)
            gbox.addWidget(control, row, 1)
        row += 1
        gbox.addItem(QtWidgets.QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding), row, 0)
        row += 1

        self.cmdTrainGmm = QtWidgets.QPushButton("Train GMM")
        self.cmdTrainHmm = QtWidgets.QPushButton("Train HMM")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.cmdTrainGmm)
        hbox.addWidget(self.cmdTrainHmm)
        gbox.addLayout(hbox, row, 0, 1, 2)

    def connect(self):
        self.setup_training_thread()
        self.cmdTrainGmm.clicked.connect(self.controller.train_gmm)
        self.controller.gmmTrainingThread.trainingStarted.connect(lambda: self.cmdTrainGmm.setEnabled(False))
        self.controller.gmmTrained.connect(lambda: self.cmdTrainGmm.setEnabled(True))

    def setup_training_thread(self):
        self.controller.gmmTrainingThread = threads.AutoBaselineModelGmmTrainingThread(self.controller, self)
        self.controller.gmmTrainingThread.trainingFinished.connect(self.controller.gmmTrained.emit)


class BaselineGmmCanvas(plots.QtCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.sampleSize = None
        self.ax = self.fig.add_subplot(1,1,1)

        self.controller.gmmTrained.connect(self.update_plots)
        self.controller.gmmTrainingThread.sampleSizeSet.connect(self.set_sample_size)

    def set_sample_size(self, val):
        self.nPoints = val

    def update_plots(self):
        gmmSample = self.controller.model.draw_gmm_samples(nDraws=5, nPoints=self.nPoints)
        self.ax.cla()
        xlim = [0, 0]
        ymin = 0
        for sample in gmmSample:
            kt, edges = np.histogram(sample, bins=100, density=True)
            binWidth = np.diff(edges[:2])
            x = edges[:-1] + binWidth/2

            xlim[0] = np.min((xlim[0], x[0]))
            xlim[1] = np.max((xlim[1], x[-1]))
            ymin = np.max((ymin, kt[np.where(kt!=0)].min()))

            self.ax.plot(x, kt, '#cccccc')

        x = np.linspace(*xlim, num=300)
        gs = self.controller.model.gmm_p_X(x)
        G = gs.sum(axis=0)
        for j, g in enumerate(gs):
            color = "b" if self.controller.model.mu[j] < self.controller.model.baselineCutoff else "r"
            self.ax.plot(x, g, color)
        self.ax.plot(x, G, "#555555")

        self.ax.set_yscale('log')
        self.ax.set_ylim(ymin, G.max()*1.1)
        self.draw()


class BaselineHmmCanvas(plots.QtCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.ax = self.fig.add_subplot(1,1,1, projection="total")
