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


class BaseResultsDialog(QDialog):
    def __init__(self, experiment, title, canvas, parent=None):
        self.experiment = experiment

        super().__init__(parent)
        self.setWindowTitle(f"Results: {title}")
        self.setFixedWidth(1000)
        self.setFixedHeight(600)
        self.setModal(True)
        self.setStyleSheet(main_stylesheet)
        self._setup(canvas)

    def _setup(self, canvas):
        box = QtWidgets.QHBoxLayout()
        box.addWidget(canvas, stretch=1)

        side_panel = QtWidgets.QGridLayout()
        side_panel.addItem(
            QtWidgets.QSpacerItem(200, 0, QSizePolicy.Fixed, QSizePolicy.Fixed), 0, 0, 1, 2
        )
        box.addLayout(side_panel)

        self.setLayout(box)
        self.layout(side_panel, canvas)


class SplitHistogramDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        super().__init__(
            experiment, "histogram", canvases.SplitHistogramCanvas(None), parent=parent
        )

    def layout(self, side_panel, canvas):
        bins = QtWidgets.QSpinBox(minimum=10, maximum=500, value=100)
        side_panel.addWidget(QtWidgets.QLabel("# bins: "), 1, 0)
        side_panel.addWidget(bins, 1, 1)

        lower = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=-0.2)
        lower.setSingleStep(0.05)
        upper = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=1.2)
        upper.setSingleStep(0.05)
        side_panel.addWidget(QtWidgets.QLabel("lower limit: "), 2, 0)
        side_panel.addWidget(lower, 2, 1)
        side_panel.addWidget(QtWidgets.QLabel("upper limit: "), 3, 0)
        side_panel.addWidget(upper, 3, 1)

        def get_parameters():
            return {
                "n_bins": bins.value(),
                "lower_bound": lower.value(),
                "upper_bound": upper.value(),
            }

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Fixed, QSizePolicy.Expanding), 4, 0, 1, 2
        )

        snapshot = QtWidgets.QPushButton("snapshot")
        snapshot.clicked.connect(canvas.take_snapshot)
        side_panel.addWidget(snapshot, 5, 0, 1, 2)

        export = QtWidgets.QPushButton("export CSV")
        export.clicked.connect(
            lambda: canvas.export_as_csv(self.experiment, **get_parameters())
        )
        side_panel.addWidget(export, 6, 0, 1, 2)


        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 15, QSizePolicy.Fixed, QSizePolicy.Fixed), 7, 0, 1, 2
        )

        calculate = QtWidgets.QPushButton("calculate")
        calculate.setMinimumHeight(35)
        calculate.clicked.connect(
            lambda: canvas.update_plot(self.experiment, **get_parameters())
        )
        side_panel.addWidget(calculate, 8, 0, 1, 2)


class TdpDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        super().__init__(
            experiment, "transition density probability", canvases.TdpCanvas(None), parent=parent
        )

    def layout(self, side_panel, canvas):
        grid_points = QtWidgets.QSpinBox(minimum=10, maximum=500, value=100)
        side_panel.addWidget(QtWidgets.QLabel("KDE resolution: "), 1, 0)
        side_panel.addWidget(grid_points, 1, 1)

        bandwidth = QtWidgets.QDoubleSpinBox(minimum=1e-3, maximum=1, value=0.02)
        side_panel.addWidget(QtWidgets.QLabel("KDE bandwidth: "), 2, 0)
        side_panel.addWidget(bandwidth, 2, 1)

        lower = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=0)
        lower.setSingleStep(0.05)
        upper = QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=1)
        upper.setSingleStep(0.05)
        side_panel.addWidget(QtWidgets.QLabel("lower limit: "), 3, 0)
        side_panel.addWidget(lower, 3, 1)
        side_panel.addWidget(QtWidgets.QLabel("upper limit: "), 4, 0)
        side_panel.addWidget(upper, 4, 1)

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Expanding, QSizePolicy.Fixed), 5, 0, 1, 2
        )

        diagonal = QtWidgets.QCheckBox("Show diagonal")
        diagonal.setChecked(False)
        side_panel.addWidget(diagonal, 6, 0, 1, 2)

        states = QtWidgets.QCheckBox("Show fitted states")
        states.setChecked(True)
        side_panel.addWidget(states, 7, 0, 1, 2)

        contours = QtWidgets.QSpinBox(minimum=10, maximum=100, value=50)
        side_panel.addWidget(QtWidgets.QLabel("# contours: "), 8, 0)
        side_panel.addWidget(contours, 8, 1)

        def get_parameters():
            return {
                "n_grid_points": grid_points.value(),
                "lower_bound": lower.value(),
                "upper_bound": upper.value(),
                "bandwidth": bandwidth.value(),
                "n_contours": contours.value(),
                "show_diagonal": bool(diagonal.checkState()),
                "show_fitted_states": bool(states.checkState()),
            }

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Fixed, QSizePolicy.Expanding), 9, 0, 1, 2
        )

        snapshot = QtWidgets.QPushButton("snapshot")
        snapshot.clicked.connect(canvas.take_snapshot)
        side_panel.addWidget(snapshot, 10, 0, 1, 2)

        def get_export_parameters():
            return {
                "n_grid_points": grid_points.value(),
                "lower_bound": lower.value(),
                "upper_bound": upper.value(),
                "bandwidth": bandwidth.value(),
            }

        export = QtWidgets.QPushButton("export CSV")
        export.clicked.connect(
            lambda: canvas.export_as_csv(self.experiment, **get_export_parameters())
        )
        side_panel.addWidget(export, 11, 0, 1, 2)

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 15, QSizePolicy.Fixed, QSizePolicy.Expanding), 12, 0, 1, 2
        )

        calculate = QtWidgets.QPushButton("calculate")
        calculate.setMinimumHeight(35)
        calculate.clicked.connect(
            lambda: canvas.update_plot(self.experiment, **get_parameters())
        )

        side_panel.addWidget(calculate, 13, 0, 1, 2)
