# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> dialogs >> merge_experiments_dialog
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QSizePolicy
from smtirf.gui import widgets


class MergeExperimentsDialog(QtWidgets.QDialog):

    filesUpdated = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filenames = set()
        self.layout()
        self.connect()

        # TODO => set OK enable only when filename is selected

        self.setWindowTitle("Merge experiments")
        self.setMinimumWidth(500)

    def layout(self):
        vbox = QtWidgets.QVBoxLayout()

        self.cmdAddFiles = QtWidgets.QPushButton("Add Files")
        self.cmdAddFiles.setIcon(QtGui.QIcon(":/icons/add.png"))
        self.cmdDelFiles = QtWidgets.QPushButton("Remove File")
        self.cmdDelFiles.setIcon(QtGui.QIcon(":/icons/delete.png"))
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.cmdAddFiles)
        hbox.addWidget(self.cmdDelFiles)
        hbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        vbox.addLayout(hbox)

        self.lstFiles = QtWidgets.QListWidget()
        vbox.addWidget(self.lstFiles)

        self.chkSelectedOnly = QtWidgets.QCheckBox("Selected traces only", checked=True)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.chkSelectedOnly)
        hbox.addItem(QtWidgets.QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        vbox.addLayout(hbox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        vbox.addWidget(buttonBox)

        self.setLayout(vbox)

    def connect(self):
        self.cmdAddFiles.clicked.connect(self.add_files)
        self.cmdDelFiles.clicked.connect(self.del_file)
        self.filesUpdated.connect(self.update_filelist)

    def add_files(self):
        fdArgs = {"caption":"Merge experiments",
                  "filter":"smTIRF Experiment (*.smtrc)"}
        filenames, filetype = QFileDialog.getOpenFileNames(**fdArgs)
        if filenames:
            for filename in filenames:
                self.filenames.add(filename)
        self.filesUpdated.emit()

    def del_file(self):
        item = self.lstFiles.currentItem()
        if item is not None:
            self.filenames.discard(item.text())
        self.filesUpdated.emit()

    def update_filelist(self):
        self.lstFiles.clear()
        for f in self.filenames:
            self.lstFiles.addItem(QtWidgets.QListWidgetItem(f))

    def get_kwargs(self):
        return {"filenames": self.filenames,
                "selectedOnly": self.chkSelectedOnly.isChecked()}
