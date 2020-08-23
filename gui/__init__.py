# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> __init__
"""
from PyQt5 import QtWidgets, QtCore, QtGui

# ==============================================================================
# config
# ==============================================================================
from . import resources


# ==============================================================================
# window base classes
# ==============================================================================
from . import resources
class SMTirfMainWindow(QtWidgets.QMainWindow):
    """ base class for GUI main window """

    def __init__(self, title="TIRF Analysis", **kwargs):
        super().__init__(windowTitle=title, **kwargs)
        self.resize(1000, 600)
        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)
        self.setWindowIcon(QtGui.QIcon(":/icons/dna.png"))
