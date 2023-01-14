from PyQt5 import QtWidgets, QtCore, QtGui
import contextlib


def set_enabler(widget, enabler):
    if enabler is not None:
        widget.setEnabled(False)
        enabler.connect(lambda: widget.setEnabled(True))


def add_popup_toolbutton(toolbar, icon, label, enabler=None):
    btn = QtWidgets.QToolButton()
    btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
    btn.setIcon(QtGui.QIcon(f":{icon}.svg"))
    btn.setText(label)
    set_enabler(btn, enabler)
    toolbar.addWidget(btn)
    return btn


def add_popup_action(btn, label, callback, shortcut=None, enabler=None):
    action = QtWidgets.QAction(label, btn.parent())
    if shortcut is not None:
        action.setShortcut(shortcut)
    with contextlib.suppress(TypeError):
        action.triggered.connect(callback)
    set_enabler(action, enabler)
    btn.addAction(action)


class MainToolbar(QtWidgets.QToolBar):
    def __init__(self, controller, import_method, open_method, save_method):
        super().__init__("main")

        btn = add_popup_toolbutton(self, "microscope", "Experiment")
        add_popup_action(btn, "Import PMA", import_method, "Ctrl+N")
        add_popup_action(btn, "Open Project", open_method, "Ctrl+O")
        add_popup_action(
            btn,
            "Save Project",
            save_method,
            "Ctrl+S",
            enabler=controller.experimentChanged,
        )

        btn = add_popup_toolbutton(
            self, "gaussian", "Results", enabler=controller.experimentChanged
        )

        btn = add_popup_toolbutton(
            self, "sort", "Sort", enabler=controller.experimentChanged
        )
        add_popup_action(btn, "By Index", lambda: controller.sort_traces("index"))
        add_popup_action(btn, "By Selected", lambda: controller.sort_traces("selected"))
        add_popup_action(
            btn, "By Correlation", lambda: controller.sort_traces("corrcoef")
        )

        btn = add_popup_toolbutton(
            self, "select", "Select", enabler=controller.experimentChanged
        )
        add_popup_action(btn, "Select All", controller.select_all)
        add_popup_action(btn, "Select None", controller.select_none)

        btn = add_popup_toolbutton(
            self, "baseline", "Baseline", enabler=controller.experimentChanged
        )

        btn = add_popup_toolbutton(self, "settings", "Settings")

        self.setIconSize(QtCore.QSize(32, 32))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setMovable(False)

        get_action = lambda a: self.widgetForAction(a).sizeHint()
        width = max([get_action(action).width() for action in self.actions()])
        height = max([get_action(action).height() for action in self.actions()]) + 10
        for action in self.actions():
            self.widgetForAction(action).setFixedSize(width, height)
