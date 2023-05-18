from PyQt6 import QtCore


class TrainGlobalThread(QtCore.QThread):
    started_training = QtCore.pyqtSignal()
    finished_training = QtCore.pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.nstates = None
        self.shared_variance = None

    def __del__(self):
        self.wait()

    def set_parameters(self, nstates, shared_variance):
        self.nstates = nstates
        self.shared_variance = shared_variance

    def run(self):
        self.started_training.emit()
        self.controller.experiment.train(
            self.nstates, shared_variance=self.shared_variance
        )
        self.finished_training.emit()
