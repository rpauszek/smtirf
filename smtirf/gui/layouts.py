from PyQt5 import QtWidgets


class ParameterLayout(QtWidgets.QGridLayout):
    def __init__(self):
        super().__init__()
        self.setColumnStretch(0, 1)
        self._current_row = 0
        self._widgets = {}

    def add_widget(self, widget, name, label, unit):
        self._widgets[name] = widget
        self.addWidget(QtWidgets.QLabel(f"{label}:"), self._current_row, 0)
        self.addWidget(widget, self._current_row, 1)
        self.addWidget(QtWidgets.QLabel(unit), self._current_row, 2)
        self._current_row += 1

    def get_params(self):
        return {key: w.value() for key, w in self._widgets.items()}
