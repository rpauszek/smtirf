# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> __init__
"""
import json, contextlib
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
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
        # for key, d in J["rcParams"].items():
        #     mpl.rc(key, **d)
        # self.colors = J["colors"]
        self.qt = J["qtParams"]

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

    @staticmethod
    def add_toolbar_button(toolbar, icon, label, callback=None, **kwargs):
        icon = QtGui.QIcon(f":/icons/{icon}.png")
        action = QtWidgets.QAction(icon, label, toolbar.parent(), **kwargs)
        with contextlib.suppress(TypeError):
            action.triggered.connect(callback)
        toolbar.addAction(action)

    @staticmethod
    def format_toolbar(toolbar):
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setIconSize(QtCore.QSize(*CONFIG.qt["TOOLBUTTON_SIZE"]))
        for action in toolbar.actions():
            widget = toolbar.widgetForAction(action)
            widget.setFixedSize(widget.sizeHint().width(), CONFIG.qt["BUTTON_HEIGHT"])
