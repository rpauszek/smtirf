# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> autobaseline_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets


class AutoBaselineDialog(QtWidgets.QDialog):

    filesUpdated = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))
        self.layout()
        self.connect()


        self.setWindowTitle("Auto-Detect Baseline")
        self.setMinimumWidth(650)

    def layout(self):
        pass

    def connect(self):
        pass
