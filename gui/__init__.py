# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> __init__
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class SMTirfMainWindow(QtWidgets.QMainWindow):
    """ base class for GUI main window """

    def __init__(self, title="TIRF Analysis", **kwargs):
        super().__init__(windowTitle=title, **kwargs)
        self.resize(1000, 600)
        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)
