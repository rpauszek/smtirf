from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


class ExperimentTypeButtonGroup(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonTypeMap = {}
        self.layout()

    def layout(self):
        self.buttonGroup = QtWidgets.QButtonGroup()

        radFretExperimentType = QtWidgets.QRadioButton("FRET")
        radPifeExperimentType = QtWidgets.QRadioButton("PIFE")
        radFretExperimentType.setChecked(True)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        for btn, key in zip((radFretExperimentType, radPifeExperimentType), ("fret", "pife")):
            hbox.addWidget(btn)
            self.buttonGroup.addButton(btn)
            self.buttonTypeMap[btn] = key
        hbox.addItem(QtWidgets.QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.setLayout(hbox)

    @property
    def experimentType(self):
        btn = self.buttonGroup.checkedButton()
        return self.buttonTypeMap[btn]
