# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> buttons
"""
from PyQt5.QtWidgets import QFileDialog, QSizePolicy
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np

__all__ = ["ToggleSelectionAction", "TrainModelButton", "TrainAllModelButton"]

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


# ==============================================================================
class BaseTrainModelButton(QtWidgets.QWidget):
    _modelStatus = {"none" : ("#eeeeee", "#000000"),
                    "ok" : ("#009ACD", "#ffffff"),
                    "error" : ("#CD2626", "#EEEE00"),
                    "working" : ("#DAA520", "#444444")}
    _modelLabels = ("Baum-Welch", "Variational Bayes")
    _modelTypes = ("em", "vb")

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.K = 2
        self.trc = None
        self.init_widgets()
        self.layout()
        self.connect()

        self.set_n_states()
        self.set_model_style("none")
        self.check_model_type()

    def init_widgets(self):
        self.cboModelTypes = QtWidgets.QComboBox()
        for item in self._modelLabels:
            self.cboModelTypes.addItem(item)

        self.cmdSubtractState = QtWidgets.QPushButton("\u2212")
        self.cmdAddState = QtWidgets.QPushButton("\u002b")
        for btn in (self.cmdSubtractState, self.cmdAddState):
            btn.setMaximumWidth(25)
        self.lblNStates = QtWidgets.QLabel("")
        self.lblNStates.setMinimumWidth(30)
        self.lblNStates.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.cmdTrain = QtWidgets.QPushButton("Train")

        self.spnRepeats = QtWidgets.QSpinBox(minimum=1, maximum=500, value=5)
        self.chkSharedVar = QtWidgets.QCheckBox("Shared Variance")

    def layout(self):
        pass

    def connect(self):
        self.cmdAddState.clicked.connect(self.add_state)
        self.cmdSubtractState.clicked.connect(self.subtract_state)
        self.cmdTrain.clicked.connect(self.train_model)

    def train_model(self):
        pass

    @property
    def modelType(self):
        return self._modelTypes[self.cboModelTypes.currentIndex()]

    @property
    def modelKwargs(self):
        kwargs =  {"K" : self.K,
                   "sharedVariance" : self.chkSharedVar.isChecked()}
        if self.cboModelTypes.isEnabled():
            kwargs["modelType"] = self.modelType
        if self.spnRepeats.isEnabled():
            kwargs["repeats"] = self.spnRepeats.value()
        return kwargs

    def check_model_type(self):
        self.spnRepeats.setEnabled(self.modelType == "vb")

    def set_n_states(self):
        self.lblNStates.setText(f"{self.K}")

    def set_model_style(self, val):
        SS = """border: 1px solid #444444;"""
        SS += f"background-color: {self._modelStatus[val][0]};"
        SS += f"color: {self._modelStatus[val][1]};"
        self.lblNStates.setStyleSheet(SS)

    def add_state(self):
        self.K += 1
        self.set_n_states()
        self.set_model_style("none")

    def subtract_state(self):
        if self.K > 2:
            self.K -= 1
            self.set_n_states()
            self.set_model_style("none")


class TrainModelButton(BaseTrainModelButton):

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        self.controller.setup_training_thread(self)

    def layout(self):
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.cboModelTypes)
        hbox.addWidget(self.cmdSubtractState)
        hbox.addWidget(self.lblNStates)
        hbox.addWidget(self.cmdAddState)
        hbox.addWidget(self.cmdTrain)
        hbox.addWidget(QtWidgets.QLabel("Repeats: "))
        hbox.addWidget(self.spnRepeats)
        hbox.addWidget(self.chkSharedVar)
        self.setLayout(hbox)

    def connect(self):
        super().connect()
        self.cboModelTypes.currentIndexChanged.connect(self.check_model_type)
        self.controller.trainingMessageChanged.connect(self.set_model_style)
        self.controller.currentTraceChanged.connect(self.update_trace)
        self.controller.modelTrained.connect(self.update_trace)

    def setEnabled(self, b):
        for w in (self.cmdAddState, self.cmdSubtractState, self.cmdTrain, self.cboModelTypes, self.chkSharedVar):
            w.setEnabled(b)
        if self.trc.classLabel == "multimer":
            self.cboModelTypes.setEnabled(False)

    def update_trace(self, trc):
        self.trc = trc
        self.check_current_model(trc)
        self.cboModelTypes.setEnabled(trc.classLabel != "multimer")
        self.update_text()

    def check_current_model(self, trc):
        try:
            i = self._modelTypes.index(trc.model.modelType)
            self.cboModelTypes.setCurrentIndex(i)
            self.chkSharedVar.setChecked(trc.model.sharedVariance)
        except (AttributeError, ValueError):
            pass

    def update_text(self):
        if self.trc.model is None:
            val = "none"
        elif np.any(np.isnan(self.trc.model.mu)):
            val = "error"
            self.K = self.trc.model.K
        else:
            val = "ok"
            self.K = self.trc.model.K
        self.set_n_states()
        self.set_model_style(val)

    def train_model(self):
        self.controller.train_trace()


class TrainAllModelButton(BaseTrainModelButton):

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller, *args, **kwargs)
        # self.controller.setup_training_thread(self)

    def layout(self):
        gbox = QtWidgets.QGridLayout()
        grpModelParams = QtWidgets.QGroupBox("Model Parameters")
        grpModelParams.setLayout(gbox)
        row = 0

        gbox.addWidget(self.cboModelTypes, row, 0)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.addWidget(self.cmdSubtractState)
        hbox.addWidget(self.lblNStates)
        hbox.addWidget(self.cmdAddState)
        gbox.addLayout(hbox, row, 1)
        row += 1

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Repeats:"), stretch=1)
        hbox.addWidget(self.spnRepeats)
        gbox.addLayout(hbox, row, 0)
        gbox.addWidget(self.chkSharedVar, row, 1)
        row += 1

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        vbox.addWidget(grpModelParams)
        self.setLayout(vbox)

    def train_model(self):
        print("train clicked")
