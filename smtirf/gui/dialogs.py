import numpy as np
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets

from . import widgets, canvases, main_stylesheet
from .controllers import ResultsController
from .panels import ResultsParamGroup


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
        self.controller = ResultsController(experiment)
        self.controller.register_canvas(canvas)

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
        self.setLayout(box)

        side_panel = QtWidgets.QVBoxLayout()
        box.addLayout(side_panel)

        side_panel.addWidget(widgets.CalculateResultsButton(self.controller))

        side_panel.addItem(
            QtWidgets.QSpacerItem(200, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )

        side_panel.addWidget(params := ResultsParamGroup(self.controller))

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Fixed, QSizePolicy.Expanding)
        )

        side_panel.addWidget(widgets.SnapshotResultsButton(self.controller))
        side_panel.addWidget(widgets.ExportResultsButton(self.controller))

        self.layout(params)


class SplitHistogramDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        super().__init__(
            experiment, "histogram", canvases.SplitHistogramCanvas(None), parent=parent
        )

    def layout(self, params):
        bins = widgets.ResultsParamSpinBox(
            self.controller, "n_bins", minimum=10, maximum=500, value=100
        )
        params.add_spinbox("# bins", bins)

        lower = widgets.ResultsParamDoubleSpinBox(
            self.controller, "lower_bound", minimum=-2, maximum=2, value=-0.2
        )
        lower.setSingleStep(0.05)
        params.add_spinbox("lower limit", lower)

        upper = widgets.ResultsParamDoubleSpinBox(
            self.controller, "upper_bound", minimum=-2, maximum=2, value=1.2
        )
        upper.setSingleStep(0.05)
        params.add_spinbox("upper limit", upper)


class TdpDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        super().__init__(
            experiment,
            "transition density probability",
            canvases.TdpCanvas(None),
            parent=parent,
        )

    def layout(self, params):
        grid_points = widgets.ResultsParamSpinBox(
            self.controller, "n_grid_points", minimum=10, maximum=500, value=100
        )
        params.add_spinbox("KDE resolution", grid_points)

        bandwidth = widgets.ResultsParamDoubleSpinBox(
            self.controller, "bandwidth", minimum=1e-3, maximum=1, value=0.02
        )
        params.add_spinbox("KDE bandwidth", bandwidth)

        lower = widgets.ResultsParamDoubleSpinBox(
            self.controller, "lower_bound", minimum=-2, maximum=2, value=-0.2
        )
        lower.setSingleStep(0.05)
        params.add_spinbox("lower limit", lower)

        upper = widgets.ResultsParamDoubleSpinBox(
            self.controller, "upper_bound", minimum=-2, maximum=2, value=1.2
        )
        upper.setSingleStep(0.05)
        params.add_spinbox("upper limit", upper)

        diagonal = widgets.ResultsParamCheckbox(
            self.controller,
            "Show diagonal",
            "show_diagonal",
            checked=False,
            on_export=False,
        )
        params.add_checkbox(diagonal)

        states = widgets.ResultsParamCheckbox(
            self.controller,
            "Show fitted states",
            "show_fitted_states",
            checked=True,
            on_export=False,
        )
        params.add_checkbox(states)

        contours = widgets.ResultsParamSpinBox(
            self.controller,
            "n_contours",
            on_export=False,
            minimum=10,
            maximum=100,
            value=50,
        )
        params.add_spinbox("# contours", contours)
