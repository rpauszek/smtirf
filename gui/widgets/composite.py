# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> composite
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy

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
