# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> trainalltraces_dialog
"""
import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets, threads

class TrainAllTracesDialog(QtWidgets.QDialog):

    trainingStarted = QtCore.pyqtSignal()
    incrementTrainedCount = QtCore.pyqtSignal()
    trainingFinished = QtCore.pyqtSignal()

    def __init__(self, expt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expt = expt
        self.thread = threads.TrainAllModelsThread(self)
        self.layout()
        self.connect()
        self.setWindowTitle("Train all selected traces")

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()
        self.modelParamsWidget = widgets.TrainAllModelButton(self)
        self.modelParamsWidget.cboModelTypes.setEnabled(self.expt.classLabel != "multimer")
        self.modelParamsWidget.cmdTrain.setEnabled(self.expt.nSelected > 0)
        self.thread.set_param_widget(self.modelParamsWidget)
        vbox.addWidget(self.modelParamsWidget)

        self.chkDeselectTraceOnError = QtWidgets.QCheckBox("Deselect trace if model training error occurs")
        self.chkDeselectTraceOnError.setEnabled(False)
        # TODO => need to implement functionality, maybe need to include in global training button
        vbox.addWidget(self.chkDeselectTraceOnError)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(TrainingTimerWidget(self))
        hbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        hbox.addWidget(self.modelParamsWidget.cmdTrain)
        vbox.addLayout(hbox)

        vbox.addItem(QtWidgets.QSpacerItem(10,30, QSizePolicy.Fixed, QSizePolicy.Fixed))
        vbox.addWidget(TrainingProgressBar(self, self.expt.nSelected))

        self.setLayout(vbox)

    def connect(self):
        self.thread.trainingStarted.connect(self.trainingStarted.emit)
        self.thread.traceTrained.connect(self.incrementTrainedCount.emit)
        self.thread.trainingFinished.connect(self.trainingFinished.emit)


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

    def __init__(self, controller, maximum):
        super().__init__(minimum=0, maximum=maximum, value=0)
        self.setFormat(r" %v/%m")
        self.setMinimumWidth(120)
        self.setStyleSheet(self.SS)
        controller.incrementTrainedCount.connect(self.increment_count)
        controller.trainingStarted.connect(lambda : self.setValue(0))

    def increment_count(self):
        self.setValue(self.value()+1)


class TrainingTimerWidget(QtWidgets.QLabel):

    def __init__(self, controller):
        super().__init__("")
        self.controller = controller
        self.count = 0 # counter in seconds

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.controller.trainingStarted.connect(self.start)
        self.controller.trainingFinished.connect(self.stop)

    def start(self):
        self.setText("")
        self.setStyleSheet("color: #FF6347; font-weight: bold;")
        self.count = 0
        self.timer.start(1000)

    def show_time(self):
        self.count += 1
        self.setText(str(datetime.timedelta(seconds=self.count)))

    def stop(self):
        self.timer.stop()
        self.setStyleSheet("color: #4B0082; font-weight: bold;")
