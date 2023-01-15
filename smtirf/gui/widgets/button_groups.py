from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


__all__ = ["ExperimentTypeButtonGroup"]


class BaseButtonGroup(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonTypeMap = {}
        self.layout()

    def layout(self):
        self.buttonGroup = QtWidgets.QButtonGroup()
        buttons, keys = self.make_buttons()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        for btn, key in zip(buttons, keys):
            hbox.addWidget(btn)
            self.buttonGroup.addButton(btn)
            self.buttonTypeMap[btn] = key
        hbox.addItem(
            QtWidgets.QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Fixed)
        )
        self.setLayout(hbox)

    def make_buttons(self):
        raise NotImplemented("base class should not be instantiated.")


class ExperimentTypeButtonGroup(BaseButtonGroup):
    def make_buttons(self):
        radFretExperimentType = QtWidgets.QRadioButton("FRET")
        radPifeExperimentType = QtWidgets.QRadioButton("PIFE")
        radFretExperimentType.setChecked(True)
        radPifeExperimentType.setEnabled(False)

        buttons = (radFretExperimentType, radPifeExperimentType)
        keys = ("fret", "pife")
        return buttons, keys

    @property
    def experimentType(self):
        btn = self.buttonGroup.checkedButton()
        return self.buttonTypeMap[btn]
