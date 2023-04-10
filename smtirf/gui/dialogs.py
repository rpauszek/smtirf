import numpy as np
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets

from . import widgets
from . import canvases
from . import main_stylesheet


class ImportPmaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import PMA experiment")
        self.setFixedWidth(600)
        self.setMaximumWidth(700)
        self.setModal(True)
        self.layout()
        self.setStyleSheet(main_stylesheet)

    def layout(self):
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Open | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.filenameLabel = widgets.FileSelectionLabel(
            caption="Select file to import", filterString="PMA traces (*.traces)"
        )
        buttonOpen = self.buttonBox.button(QDialogButtonBox.Open)
        buttonOpen.setEnabled(False)
        self.filenameLabel.filenameIsSet.connect(buttonOpen.setEnabled)

        self.experimentTypeGroup = widgets.ExperimentTypeButtonGroup()
        # TODO: bleedthrough, gammma, comments

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.filenameLabel)
        mainLayout.addWidget(self.experimentTypeGroup)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

    @property
    def importArgs(self):
        return {
            "filename": self.filenameLabel.filename,
            "experimentType": self.experimentTypeGroup.experimentType,
            "bleed": 0.05,
            "gamma": 1,
            "comments": "",
        }


class SplitHistogramDialog(QDialog):
    def __init__(self, experiment, parent=None):
        self.experiment = experiment

        super().__init__(parent)
        self.setWindowTitle("Results: histogram")
        self.setFixedWidth(800)
        self.setFixedHeight(700)
        self.setModal(True)
        self.layout()
        self.setStyleSheet(main_stylesheet)

    def layout(self):
        box = QtWidgets.QVBoxLayout()
        canvas = canvases.SplitHistogramCanvas(None)
        box.addWidget(canvas)

        hbox = QtWidgets.QHBoxLayout()
        bins = QtWidgets.QSpinBox(minimum=10, maximum=500, value=100)
        hbox.addWidget(QtWidgets.QLabel("# bins: "))
        hbox.addWidget(bins)

        lower = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=-0.2)
        lower.setSingleStep(0.05)
        upper = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=1.2)
        upper.setSingleStep(0.05)
        hbox.addWidget(QtWidgets.QLabel("limits: "))
        hbox.addWidget(lower)
        hbox.addWidget(upper)

        def get_parameters():
            return {
                "n_bins": bins.value(),
                "lower_bound": lower.value(),
                "upper_bound": upper.value(),
            }

        hbox.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Expanding, QSizePolicy.Fixed)
        )

        calculate = QtWidgets.QPushButton("calculate")
        calculate.clicked.connect(
            lambda: canvas.update_plot(self.experiment, **get_parameters())
        )

        hbox.addWidget(calculate)
        box.addLayout(hbox)
        self.setLayout(box)


class TdpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Results: histogram")
        self.setFixedWidth(800)
        self.setFixedHeight(700)
        self.setModal(True)
        self.layout()
        self.setStyleSheet(main_stylesheet)

    def layout(self):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(canvases.TdpCanvas(None))

        hbox = QtWidgets.QHBoxLayout()
        hbox.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Expanding, QSizePolicy.Fixed)
        )
        b = QtWidgets.QPushButton("calculate")
        hbox.addWidget(b)
        box.addLayout(hbox)

        self.setLayout(box)
