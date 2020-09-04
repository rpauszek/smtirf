# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> buttons
"""
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, QtCore, QtGui

__all__ = ["ToggleSelectionAction", "TrainModelButton"]

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


class TrainModelButton(QtWidgets.QWidget):
    _modelStatus = {"none" : ("#eeeeee", "#000000"),
                    "ok" : ("#009ACD", "#ffffff"),
                    "error" : ("#CD2626", "#EEEE00"),
                    "working" : ("#DAA520", "#444444")}

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.K = 2
        self.layout()
        self.connect()

        self.set_n_states()
        self.set_model_style("none")

    def layout(self):
        self.cboModelTypes = QtWidgets.QComboBox()
        for item in ("EM", "VB"):
            self.cboModelTypes.addItem(item)

        self.cmdSubtractState = QtWidgets.QPushButton("\u2212")
        self.cmdAddState = QtWidgets.QPushButton("\u002b")
        for btn in (self.cmdSubtractState, self.cmdAddState):
            # btn.setStyleSheet("font-size: 12pt;")
            btn.setMaximumWidth(25)

        self.lblNStates = QtWidgets.QLabel("")
        self.lblNStates.setMinimumWidth(30)
        self.lblNStates.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.cmdTrain = QtWidgets.QPushButton("Train")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.cboModelTypes)
        hbox.addWidget(self.cmdSubtractState)
        hbox.addWidget(self.lblNStates)
        hbox.addWidget(self.cmdAddState)
        hbox.addWidget(self.cmdTrain)
        self.setLayout(hbox)

    def connect(self):
        self.cmdAddState.clicked.connect(self.add_state)
        self.cmdSubtractState.clicked.connect(self.subtract_state)
        self.cmdTrain.clicked.connect(self.train_model)

    def set_model_style(self, val):
        SS = """border: 1px solid #444444;"""
        SS += f"background-color: {self._modelStatus[val][0]};"
        SS += f"color: {self._modelStatus[val][1]};"
        self.lblNStates.setStyleSheet(SS)

    def set_n_states(self):
        self.lblNStates.setText(f"{self.K}")

    def add_state(self):
        self.K += 1
        self.set_n_states()
        self.set_model_style("none")

    def subtract_state(self):
        if self.K > 2:
            self.K -= 1
            self.set_n_states()
            self.set_model_style("none")

    def train_model(self):
        self.set_model_style("working")
