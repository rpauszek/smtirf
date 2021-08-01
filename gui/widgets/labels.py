from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy, QFileDialog


__all__ = ["FileSelectionLabel"]


class LeftElidedLabel(QtWidgets.QLabel):

    def setText(self, s):
        s = QtGui.QFontMetrics(self.font()).elidedText(s, QtCore.Qt.ElideLeft, self.width())
        super().setText(s)


class FileSelectionLabel(QtWidgets.QWidget):
    filenameIsSet = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None, caption="", filterString=""):
        super().__init__(parent)
        self.caption = caption
        self.filter = filterString
        self._filename = ""
        self.layout()

    def layout(self):
        self.filenameLabel = LeftElidedLabel()
        self.filenameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.chooseFileButton = QtWidgets.QPushButton("Browse files")
        self.chooseFileButton.clicked.connect(self.choose_file)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.chooseFileButton)
        hbox.addWidget(self.filenameLabel)
        self.setLayout(hbox)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, s):
        self._filename = s
        self.filenameIsSet.emit(bool(self.filename))

    def choose_file(self):
        filename, _ = QFileDialog.getOpenFileName(caption=self.caption,
                                                  filter=self.filter)
        if filename:
            self.filename = filename
            self.filenameLabel.setText(filename)
