from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from . import controllers
from . import widgets


class TraceGroup(QtWidgets.QGroupBox):
    def __init__(self, controller, enabler_signal):
        super().__init__("Current Trace")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(widgets.TraceSelectionButton(controller))
        vbox.addWidget(widgets.TraceIdLabel(controller))
        vbox.addWidget(widgets.CorrelationLabel(controller))
        vbox.addWidget(widgets.ResetTraceButton(controller))
        self.setLayout(vbox)

        self.setEnabled(False)
        enabler_signal.connect(lambda: self.setEnabled(True))


class ExperimentGroup(QtWidgets.QGroupBox):
    def __init__(self, controller, enabler_signal):
        super().__init__("Experiment")
        gbox = QtWidgets.QGridLayout()
        row = 0
        gbox.addWidget(widgets.SelectedTraceCounter(controller), row, 0, 1, 2)
        row += 1
        gbox.addItem(QSpacerItem(5, 15, QSizePolicy.Fixed, QSizePolicy.Fixed), row, 0)

        row += 1
        gbox.addWidget(widgets.ResetOffsetsButton(controller), row, 0)
        gbox.addWidget(widgets.ResetLimitsButton(controller), row, 1)

        self.setLayout(gbox)

        self.setEnabled(False)
        enabler_signal.connect(lambda: self.setEnabled(True))


class ModelGroup(QtWidgets.QGroupBox):
    def __init__(self, controller, enabler_signal):
        super().__init__("Model")
        model_controller = controllers.ModelController()

        self.nstates_slider = widgets.ModelStatesSlider(model_controller)
        self.shared_var_checkbox = widgets.SharedVarCheckbox(model_controller)
        self.train_button = widgets.TrainGlobalButton(model_controller)

        spacer_settings = (4, 10, QtWidgets.QSizePolicy.Expanding, QSizePolicy.Fixed)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(widgets.RemoveProblemTracesButton(controller))
        vbox.addWidget(self.nstates_slider)
        vbox.addWidget(self.shared_var_checkbox)
        vbox.addSpacerItem(QtWidgets.QSpacerItem(*spacer_settings))
        vbox.addWidget(self.train_button)
        vbox.addSpacerItem(QtWidgets.QSpacerItem(*spacer_settings))
        vbox.addWidget(widgets.LogLikelihoodLabel(model_controller))
        vbox.addWidget(widgets.DeltaLogLikelihoodLabel(model_controller))
        vbox.addWidget(widgets.IterationsLabel(model_controller))
        vbox.addWidget(widgets.IsConvergedLabel(model_controller))
        self.setLayout(vbox)

        self.setEnabled(False)
        enabler_signal.connect(lambda: self.setEnabled(True))

        model_controller.numberOfStatesChanged.connect(
            lambda i: model_controller.set_nstates(i)
        )
        model_controller.sharedVarChanged.connect(
            lambda b: model_controller.set_shared_var(b)
        )

        model_controller.trainGlobalModel.connect(
            lambda i, b: controller.train_global(i, b)
        )
        controller.trainingStarted.connect(lambda: self.set_status(True))
        controller.trainingFinished.connect(lambda _: self.set_status(False))
        controller.trainingFinished.connect(
            lambda model: model_controller.updateExitFlag.emit(model.exit_flag)
        )

    def set_status(self, is_training):
        self.train_button.set_training_status(is_training)
        self.setEnabled(not is_training)
