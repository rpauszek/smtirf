from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
import contextlib

from . import resources

WINDOW_TITLE = "smTIRF Analysis"


class SMTirfMainWindow(QMainWindow):
    """GUI entry point"""

    def __init__(self):
        super().__init__(windowTitle=WINDOW_TITLE)
        self.resize(1000, 600)

        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)

        self.setup_toolbar()

    def setup_toolbar(self):
        self.toolbar = QtWidgets.QToolBar("main", parent=self)
        btn = add_popup_toolbutton(self.toolbar, "microscope", "Experiment")
        add_popup_action(btn, "Import PMA", None, "Ctrl+N")

        btn = add_popup_toolbutton(self.toolbar, "gaussian", "Results")
        btn = add_popup_toolbutton(self.toolbar, "settings", "Settings")
        btn = add_popup_toolbutton(self.toolbar, "baseline", "Baseline")
        btn = add_popup_toolbutton(self.toolbar, "sort", "Sort")
        btn = add_popup_toolbutton(self.toolbar, "select", "Select")

        # format
        self.toolbar.setIconSize(QtCore.QSize(32, 32))
        width = max([self.toolbar.widgetForAction(action).sizeHint().width()
                     for action in self.toolbar.actions()])
        height = max([self.toolbar.widgetForAction(action).sizeHint().height()
                      for action in self.toolbar.actions()]) + 10
        for action in self.toolbar.actions():
            w = self.toolbar.widgetForAction(action)
            w.setFixedSize(width, height)

        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.setMovable(False)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)


def add_popup_toolbutton(toolbar, icon, label):
    btn = QtWidgets.QToolButton()
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    btn.setIcon(QtGui.QIcon(f":{icon}.svg"))
    btn.setText(label)
    toolbar.addWidget(btn)
    return btn


def add_popup_action(btn, label, callback, shortcut=None):
    action = QtWidgets.QAction(label, btn.parent())
    if shortcut is not None:
        action.setShortcut(shortcut)
    with contextlib.suppress(TypeError):
        action.triggered.connect(callback)
    btn.addAction(action)
