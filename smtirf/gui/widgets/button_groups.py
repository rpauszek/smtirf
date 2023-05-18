from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QSizePolicy


__all__ = ["ExperimentTypeButtonGroup", "CountPercentButtonGroup"]


class BaseButtonGroup(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonTypeMap = {}
        self.layout()

    def layout(self):
        self.buttonGroup = QtWidgets.QButtonGroup()
        buttons, keys = self.make_buttons()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        for btn, key in zip(buttons, keys):
            hbox.addWidget(btn)
            self.buttonGroup.addButton(btn)
            self.buttonTypeMap[btn] = key
        hbox.addItem(
            QtWidgets.QSpacerItem(
                5, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
        )
        self.setLayout(hbox)

    def make_buttons(self):
        raise NotImplemented("base class should not be instantiated.")


class ExperimentTypeButtonGroup(BaseButtonGroup):
    def make_buttons(self):
        radFretExperimentType = QtWidgets.QRadioButton("FRET")
        radPifeExperimentType = QtWidgets.QRadioButton("PIFE")
        radFretExperimentType.setChecked(True)
        radPifeExperimentType.setEnabled(False)

        buttons = (radFretExperimentType, radPifeExperimentType)
        keys = ("fret", "pife")
        return buttons, keys

    @property
    def experimentType(self):
        btn = self.buttonGroup.checkedButton()
        return self.buttonTypeMap[btn]


class CountPercentButtonGroup(BaseButtonGroup):
    def __init__(self, controller, param_name, on_export=False, **kwargs):
        controller.register_parameter_widget(
            param_name, self.value, on_export=on_export
        )
        super().__init__(**kwargs)

    def make_buttons(self):
        buttons = (
            QtWidgets.QRadioButton("Counts"),
            radPercent := QtWidgets.QRadioButton("Percent"),
        )
        radPercent.setChecked(True)

        keys = ("counts", "percent")
        return buttons, keys

    @property
    def valueType(self):
        return self.buttonTypeMap[self.buttonGroup.checkedButton()]

    def value(self):
        return self.buttonTypeMap[self.buttonGroup.checkedButton()]
