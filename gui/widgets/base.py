# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> composite
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy, QFileDialog
import pathlib
import numpy as np

# ==============================================================================
class SpinSlider(QtWidgets.QWidget):

    indexChanged = QtCore.pyqtSignal(int)

    def __init__(self, label="Index:"):
        super().__init__()

        self.slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal)
        self.slider.setTracking(False)
        self.spinbox = QtWidgets.QSpinBox()

        box = QtWidgets.QHBoxLayout()
        box.setContentsMargins(5,5,5,5)
        box.addWidget(QtWidgets.QLabel(label))
        box.addWidget(self.spinbox)
        box.addWidget(self.slider)
        self.setLayout(box)
        self.setTabOrder(self.slider, self.spinbox)

        self.connect()

    def connect(self):
        self.slider.valueChanged.connect(self._update_index)
        self.spinbox.editingFinished.connect(self._update_slider)

    # ==========================================================================
    # internal event handling
    # ==========================================================================
    def _update_index(self, index):
        """ triggered when slider value is changed
            updates the spinbox value to match slider and emits widget signal """
        self.spinbox.setValue(index+1) # 0-based => 1-based
        self.indexChanged.emit(self.value())

    def _update_slider(self):
        """ triggered when spinbox editing is finished
            updates the slider value ==> cascades to _update_index() """
        self.slider.setValue(self.spinbox.value()-1)

    # ==========================================================================
    # public API
    # ==========================================================================
    def step(self, step):
        """ step index by <step> value; connect to user definied shortcuts """
        if self.isEnabled():
            self.setValue(self.value()+step)

    def refresh(self, listObj):
        self.setMaximum(len(listObj))
        self.indexChanged.emit(self.value())
        self.setEnabled(True)

    # ==========================================================================
    # re-implement PyQt interface
    # ==========================================================================
    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)

    def setEnabled(self, value):
        self.slider.setEnabled(value)
        self.spinbox.setEnabled(value)

    def isEnabled(self):
        return self.slider.isEnabled()

    def setMaximum(self, value):
        """ accepts 1-based value: corresponds to len(obj)
            sets maximums for both widgets """
        self.slider.setMaximum(value-1) # 0-based
        self.spinbox.setMaximum(value)  # 1-based
        self.slider.setMinimum(0)
        self.spinbox.setMinimum(1)

    def setFocus(self):
        self.slider.setFocus()

# ==============================================================================
class RadioButtonGroup(QtWidgets.QWidget):

    selectionChanged = QtCore.pyqtSignal(object)

    def __init__(self, labels, keys):
        super().__init__()
        self.keys = keys

        box = QtWidgets.QHBoxLayout()
        box.setContentsMargins(0,0,0,0)
        box.addItem(QtWidgets.QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.radiogroup = QtWidgets.QButtonGroup()
        for j, label in enumerate(labels):
            rad = QtWidgets.QRadioButton(label)
            if j == 0:
                rad.setChecked(True)
            self.radiogroup.addButton(rad)
            self.radiogroup.setId(rad, j)
            box.addWidget(rad)

        self.radiogroup.buttonClicked.connect(self.selection_clicked)
        self.setLayout(box)

    def selection_clicked(self, btn):
        self.selectionChanged.emit(self.value())

    def value(self):
        return self.keys[self.radiogroup.checkedId()]

    def setEnabled(self, b):
        for btn in self.radiogroup.buttons():
            btn.setEnabled(b)

    def isEnabled(self):
        return self.radiogroup.buttons()[0].isEnabled()

# ==============================================================================
class PathButton(QtWidgets.QWidget):

    def __init__(self, fdArgs=None):
        super().__init__()
        self._fdArgs = fdArgs
        self._filename = ""
        self.textline = QtWidgets.QLabel("")
        self.button = QtWidgets.QPushButton("Choose File")
        self.button.setMaximumWidth(75)

        box = QtWidgets.QHBoxLayout()
        box.setContentsMargins(0,0,0,0)
        box.addWidget(self.button)
        box.addWidget(self.textline)
        self.setLayout(box)
        self.setTabOrder(self.button, self.textline)

        self.button.clicked.connect(self.on_click)

    def on_click(self):
        try:
            self._filename, filetype = QFileDialog.getOpenFileName(**self._fdArgs)
        except TypeError:
            self._filename, filetype = QFileDialog.getOpenFileName()
        # self.textline.setText(filename)
        fm = QtGui.QFontMetrics(self.textline.font())
        self.textline.setText(fm.elidedText(self._filename, QtCore.Qt.ElideLeft, self.textline.width()))

    def path(self):
        # text = self.textline.text()
        if self._filename:
            return pathlib.Path(self._filename).absolute()
        else:
            return None


# ==============================================================================
class ScientificLineEdit(QtWidgets.QLineEdit):

    def __init__(self, value=0, bottom=-np.inf, top=np.inf, decimals=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        validator = QtGui.QDoubleValidator(bottom, top, decimals)
        validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
        self.setValidator(validator)

        self.setText(str(value))
        self._format_text()
        self.editingFinished.connect(self._format_text)

    def _format_text(self):
        value = float(self.text())
        self.setText(f"{value:0.1e}")

    def value(self):
        return float(self.text())
