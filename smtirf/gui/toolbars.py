from PyQt5 import QtWidgets, QtCore, QtGui
import contextlib


class ToolButton(QtWidgets.QToolButton):
    def __init__(self, toolbar, icon, label, enabler=None):
        super().__init__()
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setIcon(QtGui.QIcon(f":{icon}.svg"))
        self.setText(label)

        if enabler is not None:
            self.setEnabled(False)
            enabler.connect(lambda: self.setEnabled(True))

        toolbar.addWidget(self)

    def add_action(self, label, callback, shortcut=None, enabler=None):
        action = QtWidgets.QAction(label, self.parent())
        if shortcut is not None:
            action.setShortcut(shortcut)
        with contextlib.suppress(TypeError):
            action.triggered.connect(callback)

        if enabler is not None:
            action.setEnabled(False)
            enabler.connect(lambda: action.setEnabled(True))

        self.addAction(action)


class MainToolbar(QtWidgets.QToolBar):
    def __init__(self, controller, import_method, open_method, save_method):
        super().__init__("main")

        btn = ToolButton(self, "microscope", "Experiment")
        btn.add_action("Import PMA", import_method, "Ctrl+N")
        btn.add_action("Open Project", open_method, "Ctrl+O")
        btn.add_action(
            "Save Project",
            save_method,
            "Ctrl+S",
            enabler=controller.experimentChanged,
        )

        btn = ToolButton(
            self, "gaussian", "Results", enabler=controller.experimentChanged
        )

        btn = ToolButton(self, "sort", "Sort", enabler=controller.experimentChanged)
        btn.add_action("By Index", lambda: controller.sort_traces("index"))
        btn.add_action("By Selected", lambda: controller.sort_traces("selected"))
        btn.add_action("By Correlation", lambda: controller.sort_traces("corrcoef"))

        btn = ToolButton(self, "select", "Select", enabler=controller.experimentChanged)
        btn.add_action("Select All", controller.select_all)
        btn.add_action("Select None", controller.select_none)

        btn = ToolButton(
            self, "baseline", "Baseline", enabler=controller.experimentChanged
        )

        btn = ToolButton(self, "settings", "Settings")

        self.setIconSize(QtCore.QSize(32, 32))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setMovable(False)

        get_action = lambda a: self.widgetForAction(a).sizeHint()
        width = max([get_action(action).width() for action in self.actions()])
        height = max([get_action(action).height() for action in self.actions()]) + 10
        for action in self.actions():
            self.widgetForAction(action).setFixedSize(width, height)
