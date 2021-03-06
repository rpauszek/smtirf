# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> autobaseline_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets, plots, threads
from smtirf.gui.controllers import NavigationController
from smtirf.util import AutoBaselineModel
import numpy as np

# TODO ==> clean up threading!! maybe new thread each time button is clicked?

class AutoBaselineController(NavigationController):

    currentTraceChanged = QtCore.pyqtSignal(object)
    experimentLoaded = QtCore.pyqtSignal(object)
    traceEdited = QtCore.pyqtSignal(object)
    cutoffSet = QtCore.pyqtSignal()

    gmmTrained = QtCore.pyqtSignal()
    hmmTrained = QtCore.pyqtSignal()

    def __init__(self, expt):
        super().__init__()
        self.expt = expt
        self.model = AutoBaselineModel(expt)
        self.gmmTrainingThread = None
        self.hmmTrainingThread = None
        self.trc = self.expt[0]

    def update_index(self, value):
        """ broadcast current trace """
        super().update_index(value)
        self.trc = self.expt[self.index]
        self.currentTraceChanged.emit(self.trc)

    def set_cutoff(self, evt):
        if evt.xdata is not None:
            self.model.baselineCutoff = evt.xdata
            self.cutoffSet.emit()

    def train_gmm(self):
        self.gmmTrainingThread.start()

    def train_hmm(self):
        self.hmmTrainingThread.start()

    # def detect_baseline(self, baselineCutoff=100, nComponents=5, nPoints=1e4,
    #                     maxIter=50, tol=1e-3, printWarnings=False,
    #                     where="first", correctOffsets=True):
    #     M = smtirf.util.AutoBaselineModel(self, baselineCutoff=baselineCutoff)
    #     M.train_gmm(nComponents=nComponents, nPoints=nPoints)
    #     M.train_hmm(maxIter=maxIter, tol=tol, printWarnings=printWarnings)
    #     for trc, sp in zip(self, M.SP):
    #         trc.set_signal_labels(sp, where=where, correctOffsets=correctOffsets)


class AutoBaselineDialog(QtWidgets.QDialog):

    filesUpdated = QtCore.pyqtSignal()

    def __init__(self, expt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = AutoBaselineController(expt)
        self.layout()
        self.connect()
        self.controller.experimentLoaded.emit(self.controller.expt)

        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))
        self.setWindowTitle("Auto-Detect Baseline")
        self.setMinimumWidth(650)

    def layout(self):
        gbox = QtWidgets.QGridLayout()
        gbox.setColumnStretch(1, 1)
        self.setLayout(gbox)

        gbox.addWidget(BaselineModelGroupBox(self.controller), 0, 0)
        gbox.addWidget(BaselineGmmCanvas(self.controller), 0, 1)
        gbox.addWidget(BaselineHmmCanvas(self.controller), 1, 0, 1, 2)
        gbox.addWidget(widgets.NavBar(self.controller), 2, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        gbox.addWidget(self.buttonBox, 3, 0, 1, 2)

    def connect(self):
        self.controller.gmmTrainingThread.trainingStarted.connect(lambda: self.buttonBox.setEnabled(False))
        self.controller.gmmTrained.connect(lambda: self.buttonBox.setEnabled(True))
        self.controller.hmmTrainingThread.trainingStarted.connect(lambda: self.buttonBox.setEnabled(False))
        self.controller.hmmTrained.connect(lambda: self.buttonBox.setEnabled(True))


class BaselineModelGroupBox(QtWidgets.QGroupBox):

    _selectionTypes = ("first", "longest", "all")
    _selectionLabels = ("First", "Longest", "All")

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

        self.cboSelectionTypes = QtWidgets.QComboBox()
        for item in self._selectionLabels:
            self.cboSelectionTypes.addItem(item)
        gbox.addWidget(QtWidgets.QLabel("Select Data Range:"), row, 0)
        gbox.addWidget(self.cboSelectionTypes, row, 1)
        row += 1

        self.chkCorrectOffsets = QtWidgets.QCheckBox("Correct offsets")
        self.chkCorrectOffsets.setChecked(True)
        gbox.addWidget(self.chkCorrectOffsets, row, 0, 1, 2)
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
        self.controller.gmmTrainingThread.trainingStarted.connect(lambda: self.cmdTrainHmm.setEnabled(False))
        self.controller.gmmTrained.connect(lambda: self.cmdTrainGmm.setEnabled(True))
        self.controller.gmmTrained.connect(lambda: self.cmdTrainHmm.setEnabled(True))
        self.cmdTrainHmm.clicked.connect(self.controller.train_hmm)
        self.controller.hmmTrainingThread.trainingStarted.connect(lambda: self.cmdTrainGmm.setEnabled(False))
        self.controller.hmmTrainingThread.trainingStarted.connect(lambda: self.cmdTrainHmm.setEnabled(False))
        self.controller.hmmTrained.connect(lambda: self.cmdTrainGmm.setEnabled(True))
        self.controller.hmmTrained.connect(lambda: self.cmdTrainHmm.setEnabled(True))

    def setup_training_thread(self):
        self.controller.gmmTrainingThread = threads.AutoBaselineModelGmmTrainingThread(self.controller, self)
        self.controller.gmmTrainingThread.trainingFinished.connect(self.controller.gmmTrained.emit)
        self.controller.hmmTrainingThread = threads.AutoBaselineModelHmmTrainingThread(self.controller, self)
        self.controller.hmmTrainingThread.trainingFinished.connect(self.controller.hmmTrained.emit)


class BaselineGmmCanvas(plots.QtCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.sampleSize = None
        self.ax = self.fig.add_subplot(1,1,1)

        self.controller.gmmTrained.connect(self.update_plots)
        self.controller.gmmTrainingThread.sampleSizeSet.connect(self.set_sample_size)
        self.mpl_connect('button_release_event', self.controller.set_cutoff)
        self.controller.cutoffSet.connect(self.update_plots)

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


class BaselineHmmCanvas(plots.ScrollableCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.ax = self.fig.add_subplot(1,1,1, projection="total")

        self.controller.hmmTrained.connect(lambda: self.update_plots(self.controller.trc))
        self.controller.currentTraceChanged.connect(self.update_plots)

    def update_plots(self, trc):
        self.ax.set_trace(trc)
        self.draw()
