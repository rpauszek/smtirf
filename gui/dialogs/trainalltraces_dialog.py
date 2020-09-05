# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> import_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets

class TrainAllTracesDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout()
        self.connect()
        self.setWindowTitle("Train all selected traces")

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()
        modelParamsWidget = widgets.TrainAllModelButton(self)
        vbox.addWidget(modelParamsWidget)

        self.chkDeselectTraceOnError = QtWidgets.QCheckBox("Deselect trace if model training error occurs")
        vbox.addWidget(self.chkDeselectTraceOnError)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        hbox.addWidget(modelParamsWidget.cmdTrain)
        vbox.addLayout(hbox)

        vbox.addItem(QtWidgets.QSpacerItem(10,30, QSizePolicy.Fixed, QSizePolicy.Fixed))
        vbox.addWidget(TrainingProgressBar(self))

        self.setLayout(vbox)

    def connect(self):
        pass


class TrainingProgressBar(QtWidgets.QProgressBar):

    SS = """ QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                }

              QProgressBar::chunk {
                background-color: #FF6347;
                width: 20px;
                }
         """

    def __init__(self, controller, parent=None):
        super().__init__(parent=parent, minimum=0, maximum=500, value=10)
        self.setFormat(r" %v/%m")
        self.setMinimumWidth(120)
        self.setStyleSheet(self.SS)
