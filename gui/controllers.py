# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> controllers
"""
import pathlib
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import smtirf

class NavigationController(QtCore.QObject):

    stepIndexTriggered = QtCore.pyqtSignal(int)

    def update_index(self, value):
        """ handles indexChanged events from widgets;
            sets internal index broadcast current trace """
        self.index = value


class ExperimentController(NavigationController):
    # navigation
    currentTraceChanged = QtCore.pyqtSignal(object)
    currentResultViewChanged = QtCore.pyqtSignal(str)
    # file I/O
    experimentLoaded = QtCore.pyqtSignal(object)
    filenameChanged = QtCore.pyqtSignal(object)
    # MPL
    mplMotionNotifyEvent = QtCore.pyqtSignal(object)
    # data update
    traceEdited = QtCore.pyqtSignal(object)
    selectedEdited = QtCore.pyqtSignal(object)
    resultsUpdated = QtCore.pyqtSignal()
    # training
    trainingMessageChanged = QtCore.pyqtSignal(str)
    modelTrained = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.filename = None
        self.expt = None
        self.trc = None
        self.index = 0
        self.trainingThread = None

    @property
    def isReady(self):
        return self.expt is not None and self.trc is not None

    # ==========================================================================
    # navigation & threading
    # ==========================================================================
    def update_index(self, value):
        """ broadcast current trace """
        super().update_index(value)
        self.trc = self.expt[self.index]
        self.currentTraceChanged.emit(self.trc)

    def toggle_selected(self):
        self.trc.toggle()
        self.selectedEdited.emit(self.trc)

    def setup_training_thread(self, widget):
        self.trainingThread = smtirf.gui.threads.ModelTrainingThread(self, widget)
        self.trainingThread.trainingStarted.connect(lambda : self.trainingMessageChanged.emit("working"))
        self.trainingThread.trainingFinished.connect(lambda : self.modelTrained.emit(self.trc))
        self.trainingThread.trainingStarted.connect(lambda : widget.setEnabled(False))
        self.trainingThread.trainingFinished.connect(lambda : widget.setEnabled(True))

    # ==========================================================================
    # matplotlib
    # ==========================================================================
    def motion_notify(self, evt):
        """ redistribute MPL motion_notify_event """
        self.mplMotionNotifyEvent.emit(evt)

    # ==========================================================================
    # experiment
    # ==========================================================================
    def import_experiment_from_pma(self):
        dlg = smtirf.gui.dialogs.ImportExperimentDialog()
        rsp = dlg.exec_()
        if rsp:
            kwargs = dlg.get_kwargs()
            if kwargs["filename"]:
                self.expt = smtirf.Experiment.from_pma(**kwargs)
                self.filename = None
                self.filenameChanged.emit(self.filename)
                self.experimentLoaded.emit(self.expt)
                self.update_index(self.index)

    def merge_experiments(self):
        dlg = smtirf.gui.dialogs.MergeExperimentsDialog()
        rsp = dlg.exec_()
        if rsp:
            kwargs = dlg.get_kwargs()
            if kwargs["filenames"]:
                kwargs = dlg.get_kwargs()
                self.expt = smtirf.Experiment.merge(**kwargs)
                self.filename = None
                self.filenameChanged.emit(self.filename)
                self.experimentLoaded.emit(self.expt)
                self.update_index(self.index)

    def open_experiment(self):
        fdArgs = {"caption":"Load experiment",
                  "filter":"smTIRF Experiment (*.smtrc)"}
        filename, filetype = QFileDialog.getOpenFileName(**fdArgs)
        # check that filename isn't null, then load and signal
        if filename:
            filename = pathlib.Path(filename)
            self.expt = smtirf.Experiment.load(filename)
            self.filename = filename
            self.filenameChanged.emit(self.filename)
            self.experimentLoaded.emit(self.expt)
            self.update_index(self.index)

    def save_experiment(self):
        if self.filename is not None:
            msg = smtirf.gui.dialogs.SaveExperimentMessageBox()
            msg.exec_()
            val = msg.buttonRole(msg.clickedButton())

            if val == QMessageBox.YesRole:
                self.expt.save(self.filename)
            elif val == QMessageBox.NoRole:
                self.save_experiment_as()
        else:
            self.save_experiment_as()

    def save_experiment_as(self):
        fdArgs = {"caption":"Save experiment as...",
                  "filter":"smTIRF Experiment (*.smtrc)"}
        filename, filetype = QFileDialog.getSaveFileName(**fdArgs)
        if filename:
            self.filename = pathlib.Path(filename)
            self.expt.save(self.filename)
            self.filenameChanged.emit(self.filename)

    def detect_baseline(self):
        dlg = smtirf.gui.dialogs.AutoBaselineDialog(self.expt)
        rsp = dlg.exec_()
        self.traceEdited.emit(self.trc)

    def train_all_traces(self):
        dlg = smtirf.gui.dialogs.TrainAllTracesDialog(self.expt)
        rsp = dlg.exec_()
        self.modelTrained.emit(self.trc)

    def set_experiment_bleed(self):
        pass

    def set_experiment_gamma(self):
        pass

    def sort_by_index(self):
        self.expt.sort("index")
        self.update_index(self.index)

    def sort_by_selected(self):
        self.expt.sort("selected")
        self.update_index(self.index)

    def sort_by_correlation(self):
        self.expt.sort("corrcoef")
        self.update_index(self.index)

    def sort_by_cluster(self):
        self.expt.sort("cluster")
        self.update_index(self.index)

    def select_all(self):
        self.expt.select_all()
        self.selectedEdited.emit(self.trc)

    def select_none(self):
        self.expt.select_none()
        self.selectedEdited.emit(self.trc)

    def update_results(self):
        self.expt.update_results()
        self.resultsUpdated.emit()

    # ==========================================================================
    # trace
    # ==========================================================================
    def set_trace_offsets(self):
        pass

    def set_trace_offset_time_window(self, tmin, tmax):
        # TODO => should also handle this in Trace class for validation in scripts
        # if tmax-tmin > 0.5: # actually this is in SpanSelector...look up!
        self.trc.set_offset_time_window(tmin, tmax)
        self.traceEdited.emit(self.trc)

    def reset_trace_offsets(self):
        pass

    def set_trace_limits(self):
        pass

    def set_trace_start_time(self, time):
        self.trc.set_start_time(time)
        self.traceEdited.emit(self.trc)

    def set_trace_stop_time(self, time):
        self.trc.set_stop_time(time)
        self.traceEdited.emit(self.trc)

    def reset_trace_limits(self):
        pass

    def set_trace_cluster_index(self):
        pass

    def train_trace(self):
        self.trainingThread.start()

    # ==========================================================================
    # export
    # ==============================================================================
    def export_trace(self):
        fdArgs = {"caption":"Export trace as...",
                  "filter":"Data Files (*.dat)"}
        filename, filetype = QFileDialog.getSaveFileName(**fdArgs)
        # check that filename isn't null, then load and signal
        if filename:
            filename = pathlib.Path(filename)
            self.trc.export(filename)

    def export_histogram(self):
        fdArgs = {"caption":"Export histogram as...",
                  "filter":"Data Files (*.dat)"}
        filename, filetype = QFileDialog.getSaveFileName(**fdArgs)
        # check that filename isn't null, then load and signal
        if filename:
            filename = pathlib.Path(filename)
            self.expt.results.hist.export(filename)

    def export_tdp(self):
        fdArgs = {"caption":"Export TDP as...",
                  "filter":"Data Files (*.dat)"}
        filename, filetype = QFileDialog.getSaveFileName(**fdArgs)
        # check that filename isn't null, then load and signal
        if filename:
            filename = pathlib.Path(filename)
            self.expt.results.tdp.export(filename)
            