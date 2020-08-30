# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> buttons
"""
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, QtCore, QtGui

__all__ = ["ToggleSelectionAction"]

class ToggleSelectionAction(QtWidgets.QAction):

    def __init__(self, toolbar):
        ico = QtGui.QIcon(":/icons/radio_unchecked.png")
        super().__init__(ico, "Toggle", toolbar.parent(), shortcut=QtCore.Qt.Key_Space)

        toolbar.parent().controller.selectedEdited.connect(self.set_icon)
        toolbar.parent().controller.currentTraceChanged.connect(self.set_icon)
        self.triggered.connect(toolbar.parent().controller.toggle_selected)

    def set_icon(self, trc):
        ico = "radio_checked" if trc.isSelected else "radio_unchecked"
        self.setIcon(QtGui.QIcon(f":/icons/{ico}.png"))
