from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets

from .widgets.labels import FileSelectionLabel
from .widgets.button_groups import ExperimentTypeButtonGroup


class ImportPmaDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import PMA experiment")
        self.setFixedWidth(600)
        self.setMaximumWidth(700)
        self.setModal(True)
        self.layout()

    def layout(self):
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.filenameLabel = FileSelectionLabel(caption="Select file to import",
                                                filterString="PMA traces (*.traces)")
        buttonOpen = self.buttonBox.button(QDialogButtonBox.Open)
        buttonOpen.setEnabled(False)
        self.filenameLabel.filenameIsSet.connect(buttonOpen.setEnabled)

        self.experimentTypeGroup = ExperimentTypeButtonGroup()
        # TODO: bleedthrough, gammma, comments

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.filenameLabel)
        mainLayout.addWidget(self.experimentTypeGroup)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

    @property
    def importArgs(self):
        return {"filename": self.filenameLabel.filename,
                "experimentType": self.experimentTypeGroup.experimentType,
                "bleed": 0.05, "gamma": 1, "comments": ""}
