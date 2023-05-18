import numpy as np
import itertools
from dataclasses import dataclass, field
from io import BytesIO
from sklearn.neighbors import KernelDensity
from PyQt6.QtWidgets import QApplication, QFileDialog, QDialogButtonBox
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
from typing import ClassVar
from pathlib import Path

from .. import Experiment
from .dialogs import FilterTracesDialog
from . import threads


@dataclass
class ExperimentController(QObject):
    filename: str = ""
    _experiment: object = None
    _trace: object = None
    _index: int = 0
    experimentChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    traceIndexChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    traceStateChanged: ClassVar[pyqtSignal] = pyqtSignal(object)
    stepIndexTriggered: ClassVar[pyqtSignal] = pyqtSignal(int)
    mplMotionNotifyEvent: ClassVar[pyqtSignal] = pyqtSignal(object)
    trainingStarted: ClassVar[pyqtSignal] = pyqtSignal()
    trainingFinished: ClassVar[pyqtSignal] = pyqtSignal(object)

    def __post_init__(self):
        super().__init__()
        self.training_thread = threads.TrainGlobalThread(self)
        self.training_thread.started_training.connect(self.trainingStarted.emit)
        self.training_thread.finished_training.connect(
            lambda: self.trainingFinished.emit(self._get_model())
        )

    def _get_model(self):
        for trace in self.experiment:
            if trace.isSelected:
                return trace.model

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, value):
        self._experiment = value
        self.experimentChanged.emit(self.experiment)

    @property
    def trace(self):
        return self._trace

    @property
    def index(self):
        return self._index

    def set_index(self, value):
        self._index = value
        self.set_trace(self.index)

    def set_trace(self, index):
        self._trace = self.experiment[index]
        self.traceIndexChanged.emit(self.trace)

    def import_pma_file(
        self, filename, experimentType="fret", bleed=0.05, gamma=1, comments=""
    ):
        self.experiment = Experiment.from_pma(
            filename, experimentType, bleed, gamma, comments
        )
        self.filename = Path(filename).with_suffix(".smtrc")

    def open_experiment(self, filename):
        self.experiment = Experiment.load(filename)
        self.filename = Path(filename)

    def save_experiment(self, filename):
        self.experiment.save(filename)
        self.filename = Path(filename)

    def sort_traces(self, method):
        self.experiment.sort(method)
        self.set_index(self.index)

    def select_all(self):
        self.experiment.select_all()
        self.traceStateChanged.emit(self.trace)

    def select_none(self):
        self.experiment.select_none()
        self.traceStateChanged.emit(self.trace)

    def reset_limits(self):
        for trace in self.experiment:
            trace.set_limits(None)
        self.traceStateChanged.emit(self.trace)

    def reset_offsets(self):
        for trace in self.experiment:
            trace.set_offsets(None)
        self.traceStateChanged.emit(self.trace)

    def reset_trace(self):
        self.trace.set_limits(None)
        self.trace.set_offsets(None)
        self.traceStateChanged.emit(self.trace)

    def set_trace_offset_time_window(self, tmin, tmax):
        self.trace.set_offset_time_window(tmin, tmax)
        self.traceStateChanged.emit(self.trace)

    def set_trace_start_time(self, time):
        self.trace.set_start_time(time)
        self.traceStateChanged.emit(self.trace)

    def set_trace_stop_time(self, time):
        self.trace.set_stop_time(time)
        self.traceStateChanged.emit(self.trace)

    def toggle_selected(self):
        self.trace.toggle()
        self.traceStateChanged.emit(self.trace)

    def train_global(self, nstates, shared_var):
        self.training_thread.set_parameters(nstates, shared_var)
        self.training_thread.start()

    def remove_problem_traces(self):
        for trace in self.experiment:
            if trace.isSelected:
                if np.logical_or(np.any(trace.X < -0.5), np.any(trace.X > 1.5)):
                    trace.isSelected = False
        self.traceStateChanged.emit(self.trace)

    def show_results(self, dlg):
        _ = dlg.exec()

    def filter_traces(self):
        dlg = FilterTracesDialog()
        response = dlg.exec()

        if not response:
            return

        params = dlg.params
        for trace in self.experiment:
            if trace.isSelected:
                if np.logical_or(
                    np.any(trace.X < params["min_fret"]),
                    np.any(trace.X > params["max_fret"]),
                ):
                    trace.isSelected = False
                t = trace.t[trace.limits]
                if t[-1] - t[0] < params["min_length"]:
                    trace.isSelected = False
        self.traceStateChanged.emit(self.trace)


@dataclass
class ModelController(QObject):
    _nstates: int = 2
    _shared_var: bool = False
    numberOfStatesChanged: ClassVar[pyqtSignal] = pyqtSignal(int)
    sharedVarChanged: ClassVar[pyqtSignal] = pyqtSignal(bool)
    trainGlobalModel: ClassVar[pyqtSignal] = pyqtSignal(int, bool)
    updateExitFlag: ClassVar[pyqtSignal] = pyqtSignal(object)

    def __post_init__(self):
        super().__init__()

    def set_nstates(self, value):
        self._nstates = value

    def set_shared_var(self, value):
        self._shared_var = value

    def call_train_global(self):
        self.trainGlobalModel.emit(self._nstates, self._shared_var)


@dataclass
class ResultsController(QObject):
    _experiment: object = None
    _canvas: object = None
    parameters: dict = field(default_factory=dict)
    export_parameters: dict = field(default_factory=dict)

    @property
    def experiment(self):
        return self._experiment

    @property
    def canvas(self):
        return self._canvas

    def register_canvas(self, canvas):
        self._canvas = canvas

    def register_parameter_widget(self, name, value, on_export=True):
        self.parameters[name] = value
        if on_export:
            self.export_parameters[name] = value

    def get_parameters(self):
        return {name: value() for name, value in self.parameters.items()}

    def get_export_parameters(self):
        return {name: value() for name, value in self.export_parameters.items()}

    def update_plot(self):
        self.canvas.update_plot(**self.get_parameters())

    def export_results(self):
        filename, _ = QFileDialog.getSaveFileName(
            caption="Export plot data as...", filter="CSV (*.csv)"
        )

        if filename:
            header, data = self._calculate_export_data(**self.get_export_parameters())
            np.savetxt(filename, data, header=header, delimiter="\t")

    def _calculate_export_data(self, **kwargs):
        raise NotImplementedError("not implemented in base class")

    def take_snapshot(self):
        with BytesIO() as buffer:
            self.canvas.figure.savefig(buffer)
            QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))


class SplitHistogramController(ResultsController):
    def _calculate_bars(self, n_bins, lower_bound, upper_bound):
        observations = np.hstack(
            [trace.X for trace in self.experiment if trace.isSelected]
        )
        statepath = np.hstack(
            [trace.SP for trace in self.experiment if trace.isSelected]
        )
        bins = np.linspace(lower_bound, upper_bound, n_bins + 1)

        full_counts, _ = np.histogram(observations, bins)
        full_density = full_counts / np.trapz(full_counts, bins[:-1])

        state_densities = []
        fractions = []
        for state in np.unique(statepath):
            data = observations[statepath == state]
            counts, _ = np.histogram(data, bins)
            fraction = data.size / observations.size
            density = counts / np.trapz(counts, bins[:-1]) * fraction
            state_densities.append(density)
            fractions.append(fraction)

        return full_density, state_densities, fractions, bins

    def _calculate_export_data(self, n_bins=100, lower_bound=-0.2, upper_bound=1.2):
        _, states, fractions, bins = self._calculate_bars(
            n_bins, lower_bound, upper_bound
        )
        full_density = np.vstack(states).sum(axis=0)

        bin_width = np.diff(bins[:2])
        centers = bins[:-1] + (bin_width / 2)
        data = np.vstack((centers, full_density, *states)).T

        state_headers = [
            f"state {state} density ({fraction*100:0.4f}%)"
            for state, fraction in enumerate(fractions)
        ]
        header = "\t".join(["FRET (bin center)", "Full density", *state_headers])

        return header, data


class TdpController(ResultsController):
    def _calculate_tdp(self, n_grid_points, lower_bound, upper_bound, bandwidth):
        for trace in self.experiment:
            if trace.isSelected:
                model = trace.model
                break

        data = np.vstack(
            [
                trace.dwells.get_transitions(dataType="data")
                for trace in self.experiment
                if trace.isSelected and trace.dwells is not None
            ]
        )
        mesh = np.linspace(lower_bound, upper_bound, n_grid_points)
        x, y = np.meshgrid(mesh, mesh)
        coords = np.vstack((x.ravel(), y.ravel())).T
        kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth).fit(data)
        z = np.exp(kde.score_samples(coords)).reshape(x.shape)

        return x, y, z, model

    def _calculate_export_data(
        self, n_grid_points, lower_bound, upper_bound, bandwidth
    ):
        x, y, z, _ = self._calculate_tdp(
            n_grid_points, lower_bound, upper_bound, bandwidth
        )

        data = np.vstack((x.ravel(), y.ravel(), z.ravel())).T
        header = "\t".join(["initial FRET", "final FRET", "density"])

        return header, data


class StateCounterController(ResultsController):
    def _calculate_counts(self, value_type):
        if value_type not in ("counts", "percent"):
            raise ValueError(f"invalid value_type '{value_type}'")

        trace_states = [
            np.unique(trace.SP) for trace in self.experiment if trace.isSelected
        ]
        available_states = np.arange((n_states := np.max(np.hstack(trace_states)) + 1))

        combos = itertools.chain(
            *[itertools.combinations(available_states, n + 1) for n in range(n_states)]
        )
        counts = {c: 0 for c in combos}

        for trace in trace_states:
            counts[tuple(trace)] += 1

        if value_type == "percent":
            total_points = len(trace_states)
            counts = {key: value / total_points * 100 for key, value in counts.items()}

        return counts
