# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> __init__
"""
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets, QtGui

# ==============================================================================
# Message Boxes
# ==============================================================================
class SaveExperimentMessageBox(QMessageBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Save experiment?")
        self.setIconPixmap(QtGui.QPixmap(f":/lib/icons/help.png"))
        self.setText("Save changes with current filename?")

        self.addButton(QtWidgets.QPushButton("Yes"), QMessageBox.YesRole )
        self.addButton(QtWidgets.QPushButton("No"), QMessageBox.NoRole)
        self.addButton(QtWidgets.QPushButton("Cancel"), QMessageBox.RejectRole)
# ==============================================================================

from .import_dialog import ImportExperimentDialog
from .trainalltraces_dialog import TrainAllTracesDialog
from .merge_experiments_dialog import MergeExperimentsDialog
from .autobaseline_dialog import AutoBaselineDialog
