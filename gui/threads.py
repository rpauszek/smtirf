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
    sampleSizeSet = QtCore.pyqtSignal(int)

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
        self.sampleSizeSet.emit(kwargs["nPoints"])
        self.controller.model.train_gmm(**kwargs)
        self.trainingFinished.emit()


class AutoBaselineModelHmmTrainingThread(QtCore.QThread):

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
        kwargs = {"maxIter": self._parent.spnHmmMaxIter.value(),
                  "tol": self._parent.txtHmmTol.value(),
                 }
        self.controller.model.train_hmm(**kwargs)

        selectionType = self._parent._selectionTypes[self._parent.cboSelectionTypes.currentIndex()]
        print(selectionType)
        for trc, sp in zip(self.controller.expt, self.controller.model.SP):
            trc.set_signal_labels(sp, where=selectionType, correctOffsets=self._parent.chkCorrectOffsets.isChecked())

        self.trainingFinished.emit()
