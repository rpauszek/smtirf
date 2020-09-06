# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> autobaseline_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets, plots


class AutoBaselineDialog(QtWidgets.QDialog):

    filesUpdated = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout()
        self.connect()

        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))
        self.setWindowTitle("Auto-Detect Baseline")
        self.setMinimumWidth(650)

    def layout(self):
        gbox = QtWidgets.QGridLayout()
        gbox.setColumnStretch(1, 1)
        self.setLayout(gbox)

        gbox.addWidget(BaselineModelGroupBox(self), 0, 0)
        gbox.addWidget(BaselineGmmCanvas(self), 0, 1)
        gbox.addWidget(BaselineHmmCanvas(self), 1, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        gbox.addWidget(self.buttonBox, 2, 0, 1, 2)

    def connect(self):
        pass


class BaselineModelGroupBox(QtWidgets.QGroupBox):

    def __init__(self, controller):
        super().__init__("Model Parameters")
        self.layout()

    def layout(self):
        self.spnGmmComponents = QtWidgets.QSpinBox(minimum=2, maximum=50, value=10)
        self.txtGmmNPoints = widgets.base.ScientificLineEdit(1e4)
        self.spnGmmMaxIter = QtWidgets.QSpinBox(minimum=10, maximum=1e4, value=250)
        self.txtGmmTol = widgets.base.ScientificLineEdit(1e-3)
        self.spnHmmMaxIter = QtWidgets.QSpinBox(minimum=10, maximum=1e4, value=250)
        self.txtHmmTol = widgets.base.ScientificLineEdit(1e-3)

        gbox = QtWidgets.QGridLayout()
        gbox.setColumnStretch(0, 1)
        self.setLayout(gbox)
        controls = (self.spnGmmComponents, self.txtGmmNPoints,
                    self.spnGmmMaxIter, self.txtGmmTol,
                    self.spnHmmMaxIter, self.txtHmmTol)
        labels = ("GMM Components", "GMM Sample Size",
                  "GMM Max Iterations", "GMM Tolerance",
                  "HMM Max Iterations", "HMM Tolerance")
        for row, (control, label) in enumerate(zip(controls, labels)):
            control.setMaximumWidth(60)
            gbox.addWidget(QtWidgets.QLabel(label+": "), row, 0)
            gbox.addWidget(control, row, 1)
        gbox.addItem(QtWidgets.QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding), row+1, 0)


class BaselineGmmCanvas(plots.QtCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.ax = self.fig.add_subplot(1,1,1)


class BaselineHmmCanvas(plots.QtCanvas):

    def __init__(self, controller):
        super().__init__(controller)
        self.ax = self.fig.add_subplot(1,1,1, projection="total")
