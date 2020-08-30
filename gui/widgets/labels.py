# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> widgets >> labels
"""
from PyQt5 import QtWidgets, QtCore, QtGui

__all__ = ["CoordinateLabel", "TraceIdLabel", "CorrelationLabel", "SelectedItemsCounter"]

class CoordinateLabel(QtWidgets.QLabel):

    def __init__(self, controller, **kwargs):
        super().__init__("x: , y: ", **kwargs)
        self.setMinimumWidth(120)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        controller.mplMotionNotifyEvent.connect(self.update_text)

    def update_text(self, evt):
        if evt.inaxes:
            self.setText(f"x: {evt.xdata:0.2f}, y: {evt.ydata:0.2f}")
        else:
            self.setText("x: , y: ")


class TraceIdLabel(QtWidgets.QLabel):
    _label = "Trace ID: "

    def __init__(self, controller, **kwargs):
        super().__init__("", **kwargs)
        self.setMinimumWidth(150)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        controller.currentTraceChanged.connect(self.update_text)
        self.setText(self._label)

    def update_text(self, trc):
        self.setText(self._label + str(trc._id))


class CorrelationLabel(QtWidgets.QLabel):
    _label = "Correlation: "

    def __init__(self, controller, **kwargs):
        super().__init__("", **kwargs)
        self.setMinimumWidth(100)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        controller.currentTraceChanged.connect(self.update_text)
        self.setText(self._label)

    def update_text(self, trc):
        self.setText(self._label + f"{trc.corrcoef:0.3f}")


class SelectedItemsCounter(QtWidgets.QProgressBar):

    SS = """ QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                }

              QProgressBar::chunk {
                background-color: #6db500;
                width: 20px;
                }
         """

    def __init__(self, controller, parent=None):
        super().__init__(parent=parent)
        self.setFormat(r" %v/%m")
        self.setMinimumWidth(120)
        self.setStyleSheet(self.SS)

        controller.experimentLoaded.connect(self.refresh)
        controller.selectedEdited.connect(self.recount)

    def refresh(self, expt):
        self.expt = expt
        self.setMaximum(len(self.expt))
        self.recount()

    def recount(self):
        self.setValue(self.expt.nSelected)
