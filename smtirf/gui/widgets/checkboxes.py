from PyQt5 import QtWidgets

__all__ = ["SharedVarCheckbox", "ResultsParamCheckbox"]


class SharedVarCheckbox(QtWidgets.QCheckBox):
    def __init__(self, controller):
        super().__init__("shared variance")
        self.setChecked(controller._shared_var)

        # controller -> ModelController
        self.stateChanged.connect(lambda i: controller.sharedVarChanged.emit(bool(i)))


class ResultsParamCheckbox(QtWidgets.QCheckBox):
    def __init__(self, controller, label, param_name, checked=False, on_export=True):
        super().__init__(label)
        self.setChecked(checked)
        controller.register_parameter_widget(
            param_name, lambda: bool(self.checkState()), on_export=on_export
        )
