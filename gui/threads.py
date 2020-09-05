# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> threads
"""
from PyQt5 import QtWidgets, QtGui, QtCore

class ModelTrainingThread(QtCore.QThread):

    trainingStarted = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, controller, parent):
        super().__init__()
        self.controller = controller
        self._parent = parent

    def __del__(self):
        self.wait()

    def run(self):
        self.trainingStarted.emit()
        trc = self.controller.trc
        # TODO ==> use parent dict for all training arguments
        try:
            try:
                trc.train("em", self._parent.K) # !! TODO => multimer just takes K
            except ZeroDivisionError:
                pass
        except TypeError:
            try:
                trc.train(self._parent.K)
            except ZeroDivisionError:
                pass
        self.trainingFinished.emit()
