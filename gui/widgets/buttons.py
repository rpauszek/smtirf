from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ..util import confirm_click


__all__ = ["TraceSelectionButton", "ResetOffsetsButton", "ResetLimitsButton"]


class TraceSelectionButton(QtWidgets.QPushButton):

    def __init__(self, controller, **kwargs):
        super().__init__("Discarded")
        self.setMinimumHeight(35)
        self.setCheckable(True)
        self.setChecked(False)

        self.clicked.connect(controller.toggle_selected)
        self.toggled.connect(self.update_style)
        controller.traceIndexChanged.connect(lambda trace: self.setChecked(trace.isSelected))
        controller.traceStateChanged.connect(lambda trace: self.setChecked(trace.isSelected))
        self.update_style()

    def update_style(self):
        color = "#1874CD" if self.isChecked() else "#444444"
        weight = "bold" if self.isChecked() else "normal"

        self.setText("SELECTED" if self.isChecked() else "discarded")
        self.setStyleSheet(f"color: {color}; font-weight: {weight}")


class ResetOffsetsButton(QtWidgets.QPushButton):
    confirm_title = "Reset offsets?"
    confirm_message = (
        "Baseline offsets for all traces will be set to full time."
        "\nThis action cannot be reversed!"
    )

    def __init__(self, controller, **kwargs):
        super().__init__("Reset Offsets")

        @confirm_click(self.confirm_title, self.confirm_message)
        def click_callback():
            controller.reset_offsets()

        self.clicked.connect(click_callback)



class ResetLimitsButton(QtWidgets.QPushButton):
    confirm_title = "Reset limits?"
    confirm_message = (
        "Limits for all traces will be set to full time."
        "\nThis action cannot be reversed!"
    )

    def __init__(self, controller, **kwargs):
        super().__init__("Reset Limits")

        @confirm_click(self.confirm_title, self.confirm_message)
        def click_callback():
            controller.reset_limits()

        self.clicked.connect(click_callback)
