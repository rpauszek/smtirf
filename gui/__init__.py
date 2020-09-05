# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> __init__
"""
import json, contextlib
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
import matplotlib as mpl
from . import controllers

# ==============================================================================
# config
# ==============================================================================
from . import resources

class SMTirfAppConfig():

    def __init__(self):
        self.filename = Path(__file__).parent / "lib/config.json"
        with open(self.filename, "r") as F:
            J = json.loads(F.read())
        self.colors = J["colors"]
        self.rc = J["rcParams"]
        self.qt = J["qtParams"]
        self.opts = J["opts"]

        for key, d in self.rc.items():
            mpl.rc(key, **d)

CONFIG = SMTirfAppConfig()


# ==============================================================================
# window base classes
# ==============================================================================
from . import resources
class SMTirfMainWindow(QtWidgets.QMainWindow):
    """ base class for GUI main window """

    controller = controllers.ExperimentController()

    def __init__(self, title="TIRF Analysis", **kwargs):
        super().__init__(windowTitle=title, **kwargs)
        self.resize(1000, 600)
        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)
        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))


class SMTirfPanel(QtWidgets.QWidget):
    """ base class for switchable panel in MainWindow """

    def __init__(self, parent, toolbarName, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.controller = self.parent().controller
        self.toolbar = QtWidgets.QToolBar(toolbarName, parent=self)
        self.setup_toolbar()
        self.layout()

    def setup_toolbar(self):
        pass

    def layout(self):
        pass

    def unbind(self):
        self.parent().removeToolBar(self.toolbar)


# ==============================================================================
# utility functions
# ==============================================================================
def add_toolbar_button(toolbar, icon, label, callback=None, **kwargs):
    icon = QtGui.QIcon(f":/icons/{icon}.png")
    action = QtWidgets.QAction(icon, label, toolbar.parent(), **kwargs)
    with contextlib.suppress(TypeError):
        action.triggered.connect(callback)
    toolbar.addAction(action)

def add_toolbar_menu(toolbar, icon, label, actions):
    """ actions dictionary {"label": callback} """
    btn = QtWidgets.QToolButton()
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    btn.setIcon(QtGui.QIcon(f":/icons/{icon}.png"))
    btn.setText(label)
    toolbar.addWidget(btn)
    for lbl, callback in actions.items():
        action = QtWidgets.QAction(lbl, toolbar.parent())
        with contextlib.suppress(TypeError):
            action.triggered.connect(callback)
        btn.addAction(action)

def format_toolbar(toolbar):
    toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    toolbar.setMovable(False)
    toolbar.setIconSize(QtCore.QSize(*CONFIG.qt["TOOLBUTTON_SIZE"]))
    for action in toolbar.actions():
        widget = toolbar.widgetForAction(action)
        widget.setFixedSize(widget.sizeHint().width(), CONFIG.qt["BUTTON_HEIGHT"])

# ==============================================================================
from . import threads
from . import plots
from . import widgets
from . import dialogs
