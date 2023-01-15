from PyQt5 import QtWidgets

__all__ = ["SharedVarCheckbox"]

class SharedVarCheckbox(QtWidgets.QCheckBox):

    def __init__(self, controller):
        super().__init__("shared variance")
        self.setChecked(controller._shared_var)

        # controller -> ModelController
        self.stateChanged.connect(
            lambda i: controller.sharedVarChanged.emit(bool(i))
        )