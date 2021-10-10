from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QSizePolicy
from PyQt5 import QtWidgets, QtCore, QtGui
import contextlib

from . import resources
from .controllers import ExperimentController
from .dialogs import ImportPmaDialog
from .canvases import InteractiveTraceViewer
from . import widgets


WINDOW_TITLE = "smTIRF Analysis"


class SMTirfMainWindow(QMainWindow):
    """GUI entry point"""

    def __init__(self):
        super().__init__(windowTitle=WINDOW_TITLE)
        self.controller = ExperimentController()
        self.resize(1000, 600)

        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)

        self.setup_toolbar()
        self.layout()

    def setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar("main", parent=self)
        btn = add_popup_toolbutton(self.toolbar, "microscope", "Experiment")
        add_popup_action(btn, "Import PMA", self.import_pma_experiment, "Ctrl+N")
        add_popup_action(btn, "Open Project", self.open_experiment, "Ctrl+O")
        add_popup_action(btn, "Save Project", self.save_experiment, "Ctrl+S", enabler=self.controller.experimentChanged)

        btn = add_popup_toolbutton(self.toolbar, "gaussian", "Results", enabler=self.controller.experimentChanged)
        btn = add_popup_toolbutton(self.toolbar, "settings", "Settings")
        btn = add_popup_toolbutton(self.toolbar, "baseline", "Baseline", enabler=self.controller.experimentChanged)
        btn = add_popup_toolbutton(self.toolbar, "sort", "Sort", enabler=self.controller.experimentChanged)
        btn = add_popup_toolbutton(self.toolbar, "select", "Select", enabler=self.controller.experimentChanged)

        self.toolbar.setIconSize(QtCore.QSize(32, 32))
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.setMovable(False)

        get_action = lambda a: self.toolbar.widgetForAction(a).sizeHint()
        width = max([get_action(action).width() for action in self.toolbar.actions()])
        height = max([get_action(action).height() for action in self.toolbar.actions()]) + 10
        for action in self.toolbar.actions():
            self.toolbar.widgetForAction(action).setFixedSize(width, height)

        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)

    def layout(self):
        panel = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        panel.setLayout(vbox)
        self.setCentralWidget(panel)

        canvas = InteractiveTraceViewer(self.controller)
        vbox.addWidget(canvas, stretch=1)

        navbar = widgets.TraceIndexSlider(self.controller)
        vbox.addWidget(navbar)

    def import_pma_experiment(self):
        dlg = ImportPmaDialog()
        response = dlg.exec()
        if response:
            self.controller.import_pma_file(**dlg.importArgs)

    def open_experiment(self):
        filename, _ = QFileDialog.getOpenFileName(caption="Open experiment...",
                                                  filter="smtirf Experiment (*.smtrc)")
        if filename:
            self.controller.open_experiment(filename)

    def save_experiment(self):
        msg = make_messagebox("Save experiment?", "question",
                              f"Save changes with current filename?\n{self.controller.filename}",
                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        msg.exec()
        response = msg.buttonRole(msg.clickedButton())

        if response == QMessageBox.RejectRole:
            return None
        elif response == QMessageBox.YesRole:
            self.controller.save_experiment(self.controller.filename)
        elif response == QMessageBox.NoRole:
            filename, _ = QFileDialog.getSaveFileName(caption="Save experiment as...",
                                                      filter="smtirf Experiment (*.smtrc)")
            if filename:
                self.controller.save_experiment(filename)


def make_messagebox(title, icon, message, buttons):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setIconPixmap(QtGui.QPixmap(f":{icon}.svg").scaled(32, 32))
    msg.setText(message)
    msg.setStandardButtons(buttons)
    return msg


def set_enabler(widget, enabler):
    if enabler is not None:
        widget.setEnabled(False)
        enabler.connect(lambda: widget.setEnabled(True))


def add_popup_toolbutton(toolbar, icon, label, enabler=None):
    btn = QtWidgets.QToolButton()
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    btn.setIcon(QtGui.QIcon(f":{icon}.svg"))
    btn.setText(label)
    set_enabler(btn, enabler)
    toolbar.addWidget(btn)
    return btn


def add_popup_action(btn, label, callback, shortcut=None, enabler=None):
    action = QtWidgets.QAction(label, btn.parent())
    if shortcut is not None:
        action.setShortcut(shortcut)
    with contextlib.suppress(TypeError):
        action.triggered.connect(callback)
    set_enabler(action, enabler)
    btn.addAction(action)
