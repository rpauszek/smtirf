import numpy as np
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtWidgets

from . import controllers, widgets, canvases, main_stylesheet
from .layouts import ParameterLayout
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


class FilterTracesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter traces")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        self.setMaximumWidth(500)
        self.setModal(True)

        self.param_widgets = {}
        self.layout()
        self.setStyleSheet(main_stylesheet)

    def layout(self):
        self.param_box = ParameterLayout()

        self.param_box.add_widget(
            QtWidgets.QDoubleSpinBox(minimum=0, maximum=500, value=1),
            "min_length",
            "Minimum length",
            "seconds",
        )
        self.param_box.add_widget(
            QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=-0.5),
            "min_fret",
            "Minimum FRET",
            "",
        )
        self.param_box.add_widget(
            QtWidgets.QDoubleSpinBox(minimum=-2, maximum=2, value=1.5),
            "max_fret",
            "Maximum FRET",
            "",
        )

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Filter", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(self.param_box)
        mainLayout.addItem(
            QtWidgets.QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Expanding)
        )
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

    @property
    def params(self):
        return self.param_box.get_params()


class BaseResultsDialog(QDialog):
    def __init__(
        self, title, canvas, parent=None, disable_export=False, hide_params=False
    ):
        self.controller.register_canvas(canvas)

        super().__init__(parent)
        self.setWindowTitle(f"Results: {title}")
        self.setFixedWidth(1000)
        self.setFixedHeight(600)
        self.setModal(True)
        self.setStyleSheet(main_stylesheet)
        self._setup(canvas, disable_export, hide_params)

    def _setup(self, canvas, disable_export, hide_params):
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
        params.setVisible(not hide_params)

        side_panel.addItem(
            QtWidgets.QSpacerItem(10, 5, QSizePolicy.Fixed, QSizePolicy.Expanding)
        )

        side_panel.addWidget(widgets.SnapshotResultsButton(self.controller))

        side_panel.addWidget(export := widgets.ExportResultsButton(self.controller))
        export.setEnabled(not disable_export)

        self.layout(params)

    def layout(self, params):
        pass


class SplitHistogramDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        self.controller = controllers.SplitHistogramController(experiment)
        super().__init__(
            "histogram", canvases.SplitHistogramCanvas(self.controller), parent=parent
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
        self.controller = controllers.TdpController(experiment)
        super().__init__(
            "transition density probability",
            canvases.TdpCanvas(self.controller),
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


class StateCounterDialog(BaseResultsDialog):
    def __init__(self, experiment, parent=None):
        self.controller = controllers.StateCounterController(experiment)
        super().__init__(
            "state count",
            canvases.StateCounterCanvas(self.controller),
            parent=parent,
            disable_export=True,
        )

    def layout(self, params):
        value_type = widgets.CountPercentButtonGroup(self.controller, "value_type")
        params.add_buttongroup(value_type)