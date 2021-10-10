from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QFileDialog


__all__ = ["FileSelectionLabel", "TraceIdLabel", "CorrelationLabel"]


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


class TraceLabel(QtWidgets.QWidget):
    """Base widget for labels to display trace attribute information.

    Static label describing attribute is left-aligned,
    retrieved information is right aligned.
    """

    _label = ""  # static label describing information
    _get_text = lambda *_: " "  # function to retrieve text from trace instance

    def __init__(self, controller, **kwargs):
        # * instantiate widgets
        super().__init__(**kwargs)
        self._labelWidget = QtWidgets.QLabel(self._label)
        self._textWidget = QtWidgets.QLabel("")

        # * layout
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self._labelWidget)
        hbox.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Fixed))
        hbox.addWidget(self._textWidget)
        self.setLayout(hbox)

        # * align
        self.setMinimumWidth(150)
        self._labelWidget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._textWidget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # * connect
        controller.traceIndexChanged.connect(self.update_text)
        controller.traceStateChanged.connect(self.update_text)

    def update_text(self, trace):
        self._textWidget.setText(self._get_text(trace))


class TraceIdLabel(TraceLabel):
    _label = "ID: "
    _get_text = lambda _, trace: str(trace._id)


class CorrelationLabel(TraceLabel):
    _label = "Correlation: "
    _get_text = lambda _, trace: f"{trace.corrcoef:0.3f}"
