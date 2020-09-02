# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> import_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QSizePolicy
from smtirf.gui import widgets

class ImportExperimentDialog(QtWidgets.QDialog):

    _experimentTypes = ("fret", "piecewise", "pife", "multimer")
    _experimentLabels = ("FRET", "Piecewise FRET", "PIFE", "Multimer")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout()
        self.connect()

        self.setWindowTitle("Import experiment")
        # self.setMinimumWidth(500)

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()

        self.path = widgets.base.PathButton()
        vbox.addWidget(self.path)
        vbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.experimentTypes = widgets.base.RadioButtonGroup(self._experimentLabels, self._experimentTypes)
        vbox.addWidget(QtWidgets.QLabel("Experiment type:"))
        vbox.addWidget(self.experimentTypes)
        vbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(QtWidgets.QLabel("Donor bleedthrough: "))
        self.txtBleed = QtWidgets.QDoubleSpinBox()
        hb1.addWidget(self.txtBleed)
        vbox.addLayout(hb1)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(QtWidgets.QLabel("Gamma factor: "))
        self.txtGamma = QtWidgets.QDoubleSpinBox()
        hb2.addWidget(self.txtGamma)
        vbox.addLayout(hb2)

        hb3 = QtWidgets.QHBoxLayout()
        hb3.addWidget(QtWidgets.QLabel("Channel: "))
        # self.txtChannel = QtWidgets.QSpinBox()
        self.radChannel = widgets.base.RadioButtonGroup(("1", "2"), ("1", "2"))
        self.radChannel.setEnabled(False)
        hb3.addWidget(self.radChannel)
        vbox.addLayout(hb3)

        vbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        vbox.addWidget(self.buttonBox)

        self.setLayout(vbox)

    def connect(self):
        self.experimentTypes.selectionChanged.connect(print)
