from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy


__all__ = ["TraceIndexSlider"]


class SpinSlider(QtWidgets.QWidget):

    indexChanged = QtCore.pyqtSignal(int)

    def __init__(self, label):
        super().__init__()

        self.spinbox = QtWidgets.QSpinBox(minimum=1, value=1)
        self.slider = QtWidgets.QSlider(minimum=0, value=0, orientation=QtCore.Qt.Horizontal)
        self.slider.setTracking(False)
        self.cmdStepFwd = QtWidgets.QPushButton(">>")
        self.cmdStepFwd.setMaximumWidth(25)
        self.cmdStepBack = QtWidgets.QPushButton("<<")
        self.cmdStepBack.setMaximumWidth(25)
        self.widgets = [self.spinbox, self.slider, self.cmdStepBack, self.cmdStepFwd]

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(QtWidgets.QLabel(f"{label}: "))
        for w in self.widgets:
            hbox.addWidget(w)
        self.setLayout(hbox)
        self.setTabOrder(self.slider, self.spinbox)

        self.connect()

    def connect(self):
        self.slider.valueChanged.connect(self._update_index)
        self.spinbox.editingFinished.connect(self._forward_spinbox_to_slider)
        self.cmdStepFwd.clicked.connect(lambda: self.step(1))
        self.cmdStepBack.clicked.connect(lambda: self.step(-1))

    # ==========================================================================
    # internal event handling
    # ==========================================================================
    def _update_index(self, index):
        """ triggered when slider value is changed
            updates the spinbox value to match slider and emits widget signal """
        self.spinbox.setValue(index+1) # 0-based => 1-based
        self.indexChanged.emit(self.value())

    def _forward_spinbox_to_slider(self):
        # -> self.slider.valueChanged() -> self._update_index()
        self.setValue(self.spinbox.value()-1) # 1-based => 0-based

    # ==========================================================================
    # public API
    # ==========================================================================
    def step(self, step):
        """ step index by `step` value; can connect to user definied shortcuts """
        if self.isEnabled():
            self.setValue(self.value()+step)

    def refresh_limits(self, listObject):
        self.setMaximum(len(listObject))
        self.indexChanged.emit(self.value())
        self.setEnabled(True)

    # ==========================================================================
    # re-implement PyQt interface
    # ==========================================================================
    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value) # -> self.slider.valueChanged -> self._update_index

    def setEnabled(self, value):
        for w in self.widgets:
            w.setEnabled(value)

    def isEnabled(self):
        return self.slider.isEnabled()

    def setMaximum(self, value):
        """ accepts 1-based value: corresponds to len(obj)
            sets maximums for both widgets """
        self.slider.setMaximum(value-1) # 0-based
        self.spinbox.setMaximum(value)  # 1-based
        self.slider.setMinimum(0)
        self.spinbox.setMinimum(1)


class TraceIndexSlider(SpinSlider):

    def __init__(self, controller, label="Trace Index"):
        super().__init__(label=label)
        self.setEnabled(False)

        self.indexChanged.connect(controller.set_index)
        controller.experimentChanged.connect(lambda: self.setEnabled(True))
        controller.experimentChanged.connect(self.refresh_limits)
        controller.stepIndexTriggered.connect(self.step)
