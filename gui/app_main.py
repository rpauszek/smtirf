from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets


WINDOW_TITLE = "smTIRF Analysis"


class SMTirfMainWindow(QMainWindow):
    """GUI entry point"""

    def __init__(self):
        super().__init__(windowTitle=WINDOW_TITLE)
        self.resize(1000, 600)

        QtWidgets.QShortcut("Ctrl+Q", self, activated=self.close)
