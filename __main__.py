"""
@author: Raymond F. Pauszek III, Ph.D.
Single-Molecule TIRF Viewer App
"""
import sys
from PyQt5.QtWidgets import QApplication

from smtirf.gui.app_main import SMTirfMainWindow


app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
win = SMTirfMainWindow()
win.show()
sys.exit(app.exec_())
