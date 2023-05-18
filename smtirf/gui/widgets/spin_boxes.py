from PyQt6 import QtWidgets

__all__ = ["ResultsParamSpinBox", "ResultsParamDoubleSpinBox"]


class ResultsParamSpinBox(QtWidgets.QSpinBox):
    def __init__(self, controller, param_name, on_export=True, **kwargs):
        super().__init__(**kwargs)
        controller.register_parameter_widget(
            param_name, self.value, on_export=on_export
        )


class ResultsParamDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, controller, param_name, on_export=True, **kwargs):
        super().__init__(**kwargs)
        controller.register_parameter_widget(
            param_name, self.value, on_export=on_export
        )
