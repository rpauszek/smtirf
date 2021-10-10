from PyQt5 import QtWidgets


__all__ = ["TraceSelectionButton"]


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
