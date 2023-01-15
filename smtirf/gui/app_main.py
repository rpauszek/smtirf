from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QFileDialog,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5 import QtWidgets, QtCore

from . import resources
from .controllers import ExperimentController
from .dialogs import ImportPmaDialog
from .canvases import InteractiveTraceViewer
from . import widgets
from . import panels
from . import toolbars
from .util import make_messagebox
from . import lib_path


WINDOW_TITLE = "smTIRF Analysis"


class SMTirfMainWindow(QMainWindow):
    """GUI entry point"""

    def __init__(self):
        super().__init__(windowTitle=WINDOW_TITLE)
        self.controller = ExperimentController()
        self.resize(1000, 600)

        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)
        QtWidgets.QShortcut(
            QtCore.Qt.Key_Space, self, activated=self.controller.toggle_selected
        )

        self.toolbar = toolbars.MainToolbar(
            self.controller,
            self.import_pma_experiment,
            self.open_experiment,
            self.save_experiment,
        )
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self.layout()

        with open(lib_path / "default.css", "r") as f:
            self.setStyleSheet(f.read())

    def layout(self):
        panel = QtWidgets.QWidget()
        self.setCentralWidget(panel)

        main_grid = QtWidgets.QGridLayout()
        main_grid.addWidget(InteractiveTraceViewer(self.controller), 0, 0)
        main_grid.addWidget(widgets.TraceIndexSlider(self.controller), 1, 0)

        right_vbox = QtWidgets.QVBoxLayout()
        right_vbox.addSpacerItem(
            QSpacerItem(200, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        )
        right_vbox.addWidget(
            panels.TraceGroup(self.controller, self.controller.experimentChanged)
        )
        right_vbox.addWidget(
            panels.ExperimentGroup(self.controller, self.controller.experimentChanged)
        )
        right_vbox.addWidget(
            panels.ModelGroup(self.controller, self.controller.experimentChanged)
        )
        right_vbox.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)
        )
        right_vbox.addWidget(widgets.CoordinateLabel(self.controller))
        main_grid.addLayout(right_vbox, 0, 1, 2, 1)

        main_grid.setRowStretch(0, 1)
        main_grid.setColumnStretch(0, 1)
        panel.setLayout(main_grid)

    def import_pma_experiment(self):
        dlg = ImportPmaDialog()
        response = dlg.exec()
        if response:
            self.controller.import_pma_file(**dlg.importArgs)

    def open_experiment(self):
        filename, _ = QFileDialog.getOpenFileName(
            caption="Open experiment...", filter="smtirf Experiment (*.smtrc)"
        )
        if filename:
            self.controller.open_experiment(filename)

    def save_experiment(self):
        msg = make_messagebox(
            "Save experiment?",
            "question",
            f"Save changes with current filename?\n{self.controller.filename}",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )
        msg.exec()
        response = msg.buttonRole(msg.clickedButton())

        if response == QMessageBox.RejectRole:
            return None
        elif response == QMessageBox.YesRole:
            self.controller.save_experiment(self.controller.filename)
        elif response == QMessageBox.NoRole:
            filename, _ = QFileDialog.getSaveFileName(
                caption="Save experiment as...", filter="smtirf Experiment (*.smtrc)"
            )
            if filename:
                self.controller.save_experiment(filename)
