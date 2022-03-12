from PyQt5 import QtWidgets, QtCore
from ..canvases import QtCanvas


class AutobaselineApp(QtWidgets.QWidget):

    def __init__(self):
        super().__init__(windowTitle="Automated Baseline Estimation")
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.controller = AutobaselineController()
        self.layout()

        self.show()

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(AutobaselineParametersGroup())
        hbox.addWidget(BaselineGmmCanvas(self.controller))

        vbox.addLayout(hbox)
        vbox.addWidget(BaselineTraceCanvas(self.controller))


class AutobaselineParametersGroup(QtWidgets.QGroupBox):

    def __init__(self):
        super().__init__("Detection Parameters")


class BaselineGmmCanvas(QtCanvas):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)


class BaselineTraceCanvas(QtCanvas):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)


class AutobaselineController(QtCore.QObject):

    def __init__(self):
        pass