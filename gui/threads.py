# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> threads
"""
from PyQt5 import QtWidgets, QtGui, QtCore

class ModelTrainingThread(QtCore.QThread):

    trainingStarted = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, controller, parent): # TODO => should probably rename parent
        super().__init__()
        self.controller = controller
        self._parent = parent

    def __del__(self):
        self.wait()

    def run(self):
        self.trainingStarted.emit()
        trc = self.controller.trc
        kwargs = self._parent.modelKwargs
        try:
            trc.train(**kwargs)
        except ZeroDivisionError:
            pass
        self.trainingFinished.emit()


class TrainAllModelsThread(QtCore.QThread):

    trainingStarted = QtCore.pyqtSignal()
    traceTrained = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, controller, paramWidget=None):
        super().__init__()
        self.controller = controller
        self._widget = paramWidget

    def set_param_widget(self, w):
        self._widget = w

    def __del__(self):
        self.wait()

    def run(self):
        self.trainingStarted.emit()
        kwargs = self._widget.modelKwargs
        for trc in self.controller.expt:
            if trc.isSelected:
                try:
                    trc.train(**kwargs)
                except ZeroDivisionError:
                    pass
                self.traceTrained.emit()
        self.trainingFinished.emit()


class AutoBaselineModelGmmTrainingThread(QtCore.QThread):

    trainingStarted = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, controller, parent): # TODO => should probably rename parent
        super().__init__()
        self.controller = controller
        self._parent = parent

    def __del__(self):
        self.wait()

    def run(self):
        self.trainingStarted.emit()
        kwargs = {"nComponents": self._parent.spnGmmComponents.value(),
                  "nPoints": self._parent.txtGmmNPoints.value(),
                  # "gmmMaxIter": self.spnGmmMaxIter.value(),
                  # "gmmTol": self.txtGmmTol.value(),
                 }
        self.controller.model.train_gmm(**kwargs)
        self.trainingFinished.emit()
