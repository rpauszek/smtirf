from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from . import widgets


class TraceGroup(QtWidgets.QGroupBox):
    def __init__(self, controller, enabler_signal):
        super().__init__("Current Trace")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(widgets.TraceSelectionButton(controller))
        vbox.addWidget(widgets.TraceIdLabel(controller))
        vbox.addWidget(widgets.CorrelationLabel(controller))
        self.setLayout(vbox)

        self.setEnabled(False)
        enabler_signal.connect(lambda: self.setEnabled(True))


class ExperimentGroup(QtWidgets.QGroupBox):
    def __init__(self, controller, enabler_signal):
        super().__init__("Experiment")
        gbox = QtWidgets.QGridLayout()
        row = 0
        gbox.addWidget(widgets.SelectedTraceCounter(controller), row, 0, 1, 2)
        row += 1
        gbox.addItem(QSpacerItem(5, 15, QSizePolicy.Fixed, QSizePolicy.Fixed), row, 0)

        row += 1
        gbox.addWidget(widgets.ResetOffsetsButton(controller), row, 0)
        gbox.addWidget(widgets.ResetLimitsButton(controller), row, 1)

        self.setLayout(gbox)

        self.setEnabled(False)
        enabler_signal.connect(lambda: self.setEnabled(True))
