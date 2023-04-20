import numpy as np
import io
from sklearn.neighbors import KernelDensity
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette, QImage

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

from . import config
from .axes import TraceAxes


# ==============================================================================
# base canvas classes
# ==============================================================================
class QtCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure()
        super().__init__(self.figure)
        bgcolor = QtWidgets.QWidget().palette().color(QPalette.Background)
        self.figure.set_facecolor(np.array(bgcolor.getRgb()[:-1]) / 255)
        self.figure.set_tight_layout(True)


class InteractiveTraceViewer(QtCanvas):
    traceChanged = pyqtSignal(object, bool)
    modelChanged = pyqtSignal(object, bool)
    baselineSelected = pyqtSignal(float, float)
    axes = {"selection": None, "channels": None, "total": None}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.gs = self.figure.add_gridspec(3, 1)

        controller.experimentChanged.connect(self.make_axes)
        controller.traceIndexChanged.connect(
            lambda trace: self.update_plots(trace, True)
        )
        controller.traceStateChanged.connect(
            lambda trace: self.update_plots(trace, False)
        )
        controller.trainingFinished.connect(
            lambda: self.update_plots(self.controller.trace, False)
        )
        self.mpl_connect(
            "scroll_event",
            lambda evt: controller.stepIndexTriggered.emit(int(evt.step)),
        )
        self.mpl_connect("button_release_event", self.on_release)
        self.mpl_connect(
            "motion_notify_event",
            lambda evt: self.controller.mplMotionNotifyEvent.emit(evt),
        )
        self.baselineSelected.connect(controller.set_trace_offset_time_window)

    def make_axes(self):
        for j, (dataType, ax) in enumerate(self.axes.items()):
            if ax is not None:
                ax.remove()
            projection = TraceAxes(parent=self, dataType=dataType)
            self.axes[dataType] = self.figure.add_subplot(
                self.gs[j], projection=projection
            )
        self.make_span_selectors()

    def make_span_selectors(self):
        def on_zoom(xmin, xmax):
            if xmax - xmin < 1:
                return
            for _, ax in self.axes.items():
                ax.set_xlim(xmin, xmax)
            self.draw()

        self.zoomSpan = SpanSelector(
            self.axes["selection"],
            on_zoom,
            "horizontal",
            useblit=True,
            button=1,
            props=config.spans.zoom,
        )

        self.baselineSpan = SpanSelector(
            self.axes["total"],
            self.baselineSelected.emit,
            "horizontal",
            minspan=0.5,
            useblit=True,
            button=1,
            props=config.spans.baseline,
        )

    def update_plots(self, trace, relim):
        self.traceChanged.emit(trace, relim)
        self.draw()

    def on_release(self, evt):
        """Handle mouse button release events."""

        def reset_xlim():
            for _, ax in self.axes.items():
                ax.autoscale(enable=True, axis="x")
            self.draw()

        # In selected data axes
        if evt.inaxes == self.axes["selection"] and evt.button == 3:
            reset_xlim()

        # In channel data axes
        if evt.inaxes == self.axes["channels"] and evt.xdata is not None:
            if evt.button == 1:  # start
                self.controller.set_trace_start_time(evt.xdata)
            elif evt.button == 3:  # stop
                self.controller.set_trace_stop_time(evt.xdata)


class SplitHistogramCanvas(QtCanvas):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1)

    def _calculate_bars(self, experiment, n_bins, lower_bound, upper_bound):
        observations = np.hstack([trace.X for trace in experiment if trace.isSelected])
        statepath = np.hstack([trace.SP for trace in experiment if trace.isSelected])
        bins = np.linspace(lower_bound, upper_bound, n_bins)

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

    def update_plot(self, experiment, n_bins=100, lower_bound=-0.2, upper_bound=1.2):
        full_density, states, fractions, bins = self._calculate_bars(
            experiment, n_bins, lower_bound, upper_bound
        )
        bin_width = np.diff(bins[:2])

        self.ax.cla()

        for state, (density, fraction) in enumerate(zip(states, fractions)):
            self.ax.bar(
                bins[:-1],
                density,
                bin_width,
                alpha=0.3,
                align="edge",
                label=f"state {state} = {fraction*100:0.2f}%",
            )

        self.ax.stairs(full_density, bins, ec="k")

        self.ax.set_xlabel("FRET")
        self.ax.set_ylabel("density")
        self.ax.legend()
        self.draw()

    def take_snapshot(self):
        with io.BytesIO() as buffer:
            self.figure.savefig(buffer)
            QtWidgets.QApplication.clipboard().setImage(
                QImage.fromData(buffer.getvalue())
            )

    def export_as_csv(self, experiment, n_bins=100, lower_bound=-0.2, upper_bound=1.2):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Export plot data as...", filter="CSV (*.csv)"
        )

        if filename:
            _, states, fractions, bins = self._calculate_bars(
                experiment, n_bins, lower_bound, upper_bound
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

            np.savetxt(filename, data, header=header, delimiter="\t")


class TdpCanvas(QtCanvas):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ax = self.figure.add_subplot(1, 1, 1, aspect="equal")

    def _calculate_tdp(
        self, experiment, n_grid_points, lower_bound, upper_bound, bandwidth
    ):
        for trace in experiment:
            if trace.isSelected:
                model = trace.model
                break

        data = np.vstack(
            [
                trace.dwells.get_transitions(dataType="data")
                for trace in experiment
                if trace.isSelected and trace.dwells is not None
            ]
        )
        mesh = np.linspace(lower_bound, upper_bound, n_grid_points)
        x, y = np.meshgrid(mesh, mesh)
        coords = np.vstack((x.ravel(), y.ravel())).T
        kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth).fit(data)
        z = np.exp(kde.score_samples(coords)).reshape(x.shape)

        return x, y, z, model

    def update_plot(
        self,
        experiment,
        n_grid_points=100,
        lower_bound=-0.2,
        upper_bound=1.2,
        bandwidth=0.02,
        n_contours=20,
        show_diagonal=False,
        show_fitted_states=False,
    ):
        x, y, z, model = self._calculate_tdp(
            experiment, n_grid_points, lower_bound, upper_bound, bandwidth
        )

        self.ax.cla()
        self.ax.contourf(x, y, z, n_contours)

        if show_fitted_states:
            for mu in model.phi.mu:
                self.ax.axhline(mu, c="w", ls=":", lw=0.5)
                self.ax.axvline(mu, c="w", ls=":", lw=0.5)

        if show_diagonal:
            self.ax.plot(
                (lower_bound, upper_bound),
                (lower_bound, upper_bound),
                c="w",
                ls=":",
            )

        self.ax.set_xlabel("initial FRET")
        self.ax.set_ylabel("final FRET")

        self.draw()

    def take_snapshot(self):
        with io.BytesIO() as buffer:
            self.figure.savefig(buffer)
            QtWidgets.QApplication.clipboard().setImage(
                QImage.fromData(buffer.getvalue())
            )

    def export_as_csv(
        self,
        experiment,
        n_grid_points=100,
        lower_bound=-0.2,
        upper_bound=1.2,
        bandwidth=0.02,
    ):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Export plot data as...", filter="CSV (*.csv)"
        )

        if filename:
            x, y, z, _ = self._calculate_tdp(
                experiment, n_grid_points, lower_bound, upper_bound, bandwidth
            )

            data = np.vstack((x.ravel(), y.ravel(), z.ravel())).T
            header = "\t".join(["initial FRET", "final FRET", "density"])
            np.savetxt(filename, data, header=header, delimiter="\t")
