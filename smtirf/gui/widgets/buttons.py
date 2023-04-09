from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ..util import confirm_click


__all__ = [
    "TraceSelectionButton",
    "ResetTraceButton",
    "ResetOffsetsButton",
    "ResetLimitsButton",
    "RemoveProblemTracesButton",
    "TrainGlobalButton",
    "HistogramResultsButton",
    "TdpResultsButton",
    "DwelltimeResultsButton",
]


class TraceSelectionButton(QtWidgets.QPushButton):
    def __init__(self, controller, **kwargs):
        super().__init__("discarded")
        self.setMinimumHeight(35)
        self.setCheckable(True)
        self.setChecked(False)

        updater = lambda trace: self.setChecked(trace.isSelected)

        self.clicked.connect(controller.toggle_selected)
        self.toggled.connect(
            lambda: self.setText("SELECTED" if self.isChecked() else "discarded")
        )
        controller.traceIndexChanged.connect(updater)
        controller.traceStateChanged.connect(updater)


class ResetTraceButton(QtWidgets.QPushButton):
    def __init__(self, controller, **kwargs):
        super().__init__("Reset Trace")
        self.clicked.connect(controller.reset_trace)


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


class RemoveProblemTracesButton(QtWidgets.QPushButton):
    def __init__(self, controller):
        super().__init__("Remove Problem Traces")
        self.clicked.connect(controller.remove_problem_traces)


class TrainGlobalButton(QtWidgets.QPushButton):
    def __init__(self, controller):
        super().__init__("")
        self.set_training_status(False)
        self.clicked.connect(controller.call_train_global)

    def set_training_status(self, is_training):
        label = "training..." if is_training else "Train Experiment"
        self.setText(label)


class HistogramResultsButton(QtWidgets.QPushButton):
    def __init__(self, controller):
        super().__init__("Histogram")
        self.clicked.connect(lambda: controller.show_results("hist"))


class TdpResultsButton(QtWidgets.QPushButton):
    def __init__(self, controller):
        super().__init__("Transition Density Plot")
        self.clicked.connect(lambda: controller.show_results("tdp"))


class DwelltimeResultsButton(QtWidgets.QPushButton):
    def __init__(self, controller):
        super().__init__("Dwell Times")
        self.clicked.connect(lambda: controller.show_results("dwell"))
