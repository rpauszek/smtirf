# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> sliders
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from . import composite

__all__ = ["NavBar"]

class NavBar(composite.SpinSlider):

    def __init__(self, controller, label="Trace Index:"):
        self.controller = controller
        super().__init__(label=label)
        self.setEnabled(False)

    def connect(self):
        super().connect()
        self.indexChanged.connect(self.controller.update_index)
        self.controller.experimentLoaded.connect(self.refresh)
        self.controller.stepIndexTriggered.connect(self.step)
